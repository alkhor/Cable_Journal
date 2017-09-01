from django.shortcuts import render, render_to_response
import re
import os
from . import ping_10
from connections.models import Discover_data

from ipaddress import ip_network
import os, re, multiprocessing, subprocess, time, pysnmp

# Create your views here.
def connections(request):
    num_db = Discover_data.objects.all().values()
    return render(request, 'connections.html', {'num_db': num_db})

def connections_last(request):
    num_db = Discover_data.objects.all().values()
    return render(request, 'connections.html', {'num_db': num_db})

def connections_real(request):
    switch_list = {"sstc_805_2": "172.16.5.4", "sstc_805_1": "172.16.5.9"}
    def ip_list(ip_net):
        all_hosts = list(ip_network(ip_net).hosts())
        devices = map(lambda x: str(x), all_hosts)
        return devices

    def ping(host, mp_queue):
        response = subprocess.call(["ping", "-c", "2", "-W", '4', host], stdout=DNULL)
        if response == 0:
            print(host, 'is up!')
            result = True
        else:
            print(host, 'is down!')
            result = False
        mp_queue.put((result, host))

    def worker(devices):
        mp_queue = multiprocessing.Queue()
        processes = []
        for device in devices:
            p = multiprocessing.Process(target=ping, args=(device, mp_queue))
            time.sleep(0.04)
            processes.append(p)
            p.start()
        for p in processes:
            # p.join()
            results = {True: [], False: []}  # not need
        # result = defaultdict(list)
        for p in processes:
            key, value = mp_queue.get()
            results[key] += [value]
            # result[key].append(value)
        return results[True], results[False]  # results

    def num(num):
        numbers = []
        for i in range(1, int((len(num)) + 1)):
            numbers.append(i)
        return numbers

    def num_ip(num_ip):
        numbers = num(success)
        num_ip = {}
        for x, y in zip(numbers, success):
            num_ip[x] = [y]
        return num_ip

    def create_dict(keys, values):
        return dict(zip(keys, values + [None] * (len(keys) - len(values))))

    def get_arp_all():
        from pysnmp.entity.rfc3413.oneliner import cmdgen
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget(('172.16.5.92', 161)),
            '.1.3.6.1.2.1.4.22.1.2')
        mac_list = []
        for i in varBinds:
            for ip, mac in i:
                mac_list.append(mac.prettyPrint())
        clean_mac_list = []
        for i in mac_list:
            i = i[2:][0:2] + ":" + i[2:][2:4] + ":" + i[2:][4:6] + ":" + i[2:][6:8] + ":" + i[2:][8:10] + ":" + i[2:][
                                                                                                                10:12]
            clean_mac_list.append(i)
        ip_list = []
        for i in varBinds:
            for ip, mac in i:
                ip_list.append(ip.prettyPrint())
        clean_ip_list = []
        for i in ip_list:
            clean_ip = ''.join(re.findall(r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$', i))
            clean_ip_list.append(clean_ip)
        ip_mac_dict = create_dict(clean_ip_list, clean_mac_list)
        return ip_mac_dict, clean_ip_list, clean_mac_list

    def merge_ip_mac_in_list():
        c = []
        ip_mac_dict, ip, mac = get_arp_all()
        ip_mac_list = []
        for i in range(0, len(ip)):
            ip_mac = []
            ip_mac.append(ip[i])
            ip_mac.append(mac[i])
            ip_mac_list.append(ip_mac)
        return ip_mac_list

    from pysnmp.entity.rfc3413.oneliner import cmdgen
    cmdGen = cmdgen.CommandGenerator()
    port_mac = {}

    def port_mac_dict(port, varBinds):
        c = []
        for i in varBinds:
            for a, b in i:
                c.append(b.prettyPrint())
            port_mac[port] = c

    def port_mac_switch():
        c = []
        for port in range(1, 52):
            errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(
                cmdgen.CommunityData('public'),
                cmdgen.UdpTransportTarget(('172.16.5.4', 161)),
                '1.3.6.1.4.1.11.2.14.11.5.1.9.4.2.1.2.' + str(port))
            port_mac_dict(port, varBinds)
        for i in [i for i in port_mac.keys()]:
            if len(port_mac.get(i)) <= 3:
                pass
            else:
                del port_mac[i]
        for i in [i for i in port_mac.keys()]:
            for j in port_mac.get(i):
                port_mac[i] = j[2:][0:2] + ":" + j[2:][2:4] + ":" + j[2:][4:6] + ":" + j[2:][6:8] + ":" + j[2:][8:10] + ":" + j[2:][10:12]
        return port_mac

    DNULL = open(os.devnull, 'w')
    success, failed = worker(ip_list('192.168.10.0/23'))

    def active_ip_mac_dict():
        ip_mac_dict = get_arp_all()[0]
        active_ip_mac = {}
        for i in success:
            active_ip_mac[i] = ip_mac_dict[i]
        return active_ip_mac

    all_ip_mac_dict = get_arp_all()[0]
    active_ip_mac_list = []
    for i in success:
        c = []
        c.append(i)
        c.append(all_ip_mac_dict.get(i))
        active_ip_mac_list.append(c)

    port_mac = port_mac_switch()
    list_keys = list(port_mac.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac[j]:
                i.append(j)
                i.append("sstc_805_2")

    nums = num(success)
    num = {}
    for i in nums:
        num[i] = active_ip_mac_list[i - 1]

    num_db = Discover_data.objects.all().values()

    for i in range(1, len(Discover_data.objects.values()) + 1):
        Discover_data.objects.filter(num=i).delete()

    for i in range(1,len(num)):
        if len(num.get(i)) == 2:
            new_Disc = Discover_data(num=i, ip=num.get(i)[0], mac= num.get(i)[1])
        else:
            new_Disc = Discover_data(num=i, ip=num.get(i)[0], mac=num.get(i)[1], port=num.get(i)[2], switch=num.get(i)[3])
        new_Disc.save()

    return render(request, 'connections.html', {'num': num, 'num_db': num_db})
