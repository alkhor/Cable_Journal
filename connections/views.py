from django.shortcuts import render, render_to_response
from connections.models import DiscoverData
from ipaddress import ip_network
import os, re, multiprocessing, subprocess, time, pysnmp

# Create your views here.
def connections(request):
    num_db = DiscoverData.objects.all().values()
    return render(request, 'connections.html', {'num_db': num_db})

def connections_last(request):
    num_db = DiscoverData.objects.all().values()
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
            cmdgen.UdpTransportTarget(('172.16.5.92', 161)), '.1.3.6.1.2.1.4.22.1.2')
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

    def port_mac_switch_4():
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

    def port_mac_switch_9():
        import pysnmp, re
        from pysnmp.entity.rfc3413.oneliner import cmdgen
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget(('172.16.5.9', 161)),
            '1.3.6.1.2.1.17.7.1.2.2.1.2',
            ignoreNonIncreasingOid=True)

        def mac(getvar):
            macs = getvar.split('.')
            i = 0
            ma = []
            for x in range(0, 6):
                maca = macs[i]
                if len(maca) == 1:
                    a = hex(int(maca)).replace("x", "")
                else:
                    a = hex(int(maca))[2:]
                ma.append(a)
                i = i + 1
            return ma[0] + ":" + ma[1] + ":" + ma[2] + ":" + ma[3] + ":" + ma[4] + ":" + ma[5]

        port_mac = []
        for i in varBinds:
            c = []
            for a, b in i:
                c.append(b.prettyPrint())
                c.append(mac(''.join(
                    re.findall(r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$', a.prettyPrint()))))
            port_mac.append(c)

        port_mac_9 = {}
        for j in range(1, 52):
            c = []
            for i in port_mac:
                if str(j) == i[0]:
                    c.append(i[1])
            if len(c) > 0:
                port_mac_9[j] = c

        for i in [i for i in port_mac_9.keys()]:
            if len(port_mac_9.get(i)) <= 3:
                pass
            else:
                del port_mac_9[i]
        return port_mac_9

    DNULL = open(os.devnull, 'w')
    success, failed = worker(ip_list('192.168.10.0/24'))

    def active_ip_mac_dict():
        ip_mac_dict = get_arp_all()[0]
        active_ip_mac = {}
        for i in success:
            active_ip_mac[i] = ip_mac_dict[i]
        return active_ip_mac

    def port_mac_switch_13():
        c = []
        for port in range(1, 26):
            errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(cmdgen.CommunityData('public'),
                cmdgen.UdpTransportTarget(('172.16.5.13', 161)),
                '1.3.6.1.4.1.11.2.14.11.5.1.9.4.2.1.2.' + str(port))
            port_mac_dict(port, varBinds)
        for i in [i for i in port_mac.keys()]:
            if len(port_mac.get(i)) <= 3:
                pass
            else:
                del port_mac[i]
        for i in [i for i in port_mac.keys()]:
            for j in port_mac.get(i):
                port_mac[i] = j[2:][0:2] + ":" + j[2:][2:4] + ":" + j[2:][4:6] + ":" + j[2:][6:8] + ":" + j[2:][8:10] + ":" + j[2:][                                                                                                 10:12]
        return port_mac

    def port_mac_switch_23():
        import pysnmp, re
        from pysnmp.entity.rfc3413.oneliner import cmdgen
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget(('172.16.5.23', 161)),
            '1.3.6.1.2.1.17.7.1.2.2.1.2',
            ignoreNonIncreasingOid=True)

        def mac(getvar):
            macs = getvar.split('.')
            i = 0
            ma = []
            for x in range(0, 6):
                maca = macs[i]
                if len(maca) == 1:
                    a = hex(int(maca)).replace("x", "")
                else:
                    a = hex(int(maca))[2:]
                ma.append(a)
                i = i + 1
            return ma[0] + ":" + ma[1] + ":" + ma[2] + ":" + ma[3] + ":" + ma[4] + ":" + ma[5]
        port_mac = []
        for i in varBinds:
            c = []
            for a, b in i:
                c.append(b.prettyPrint())
                c.append(mac(''.join(
                    re.findall(r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$', a.prettyPrint()))))
            port_mac.append(c)
        port_mac_dict = {}
        for j in range(1, 52):
            c = []
            for i in port_mac:
                if str(j) == i[0]:
                    c.append(i[1])
            if len(c) > 0:
                port_mac_dict[j] = c
        for i in [i for i in port_mac_dict.keys()]:
            if len(port_mac_dict.get(i)) <= 3:
                pass
            else:
                del port_mac_dict[i]
        return port_mac_dict

    def port_mac_switch_8():
        import pysnmp, re
        from pysnmp.entity.rfc3413.oneliner import cmdgen
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget(('172.16.5.8', 161)),
            '1.3.6.1.2.1.17.7.1.2.2.1.2',
            ignoreNonIncreasingOid=True)
        def mac(getvar):
            macs = getvar.split('.')
            i = 0
            ma = []
            for x in range(0, 6):
                maca = macs[i]
                if len(maca) == 1:
                    a = hex(int(maca)).replace("x", "")
                else:
                    a = hex(int(maca))[2:]
                ma.append(a)
                i = i + 1
            return ma[0] + ":" + ma[1] + ":" + ma[2] + ":" + ma[3] + ":" + ma[4] + ":" + ma[5]
        port_mac = []
        for i in varBinds:
            c = []
            for a, b in i:
                c.append(b.prettyPrint())
                c.append(mac(''.join(
                    re.findall(r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$', a.prettyPrint()))))
            port_mac.append(c)
        port_mac_dict = {}
        for j in range(1, 52):
            c = []
            for i in port_mac:
                if str(j) == i[0]:
                    c.append(i[1])
            if len(c) > 0:
                port_mac_dict[j] = c
        for i in [i for i in port_mac_dict.keys()]:
            if len(port_mac_dict.get(i)) <= 3:
                pass
            else:
                del port_mac_dict[i]
        return port_mac_dict

    def port_mac_switch_6():
        c = []
        for port in range(1, 26):
            errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(cmdgen.CommunityData('public'),
                cmdgen.UdpTransportTarget(('172.16.5.6', 161)),
                '1.3.6.1.4.1.11.2.14.11.5.1.9.4.2.1.2.' + str(port))
            port_mac_dict(port, varBinds)
        for i in [i for i in port_mac.keys()]:
            if len(port_mac.get(i)) <= 3:
                pass
            else:
                del port_mac[i]
        for i in [i for i in port_mac.keys()]:
            for j in port_mac.get(i):
                port_mac[i] = j[2:][0:2] + ":" + j[2:][2:4] + ":" + j[2:][4:6] + ":" + j[2:][6:8] + ":" + j[2:][
                                                                                                          8:10] + ":" + j[
                                                                                                                        2:][
                                                                                                                        10:12]
        return port_mac

    def port_mac_switch_15():
        c = []
        for port in range(1, 26):
            errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(cmdgen.CommunityData('public'),
                cmdgen.UdpTransportTarget(('172.16.5.15', 161)),
                '1.3.6.1.4.1.11.2.14.11.5.1.9.4.2.1.2.' + str(port))
            port_mac_dict(port, varBinds)
        for i in [i for i in port_mac.keys()]:
            if len(port_mac.get(i)) <= 3:
                pass
            else:
                del port_mac[i]
        for i in [i for i in port_mac.keys()]:
            for j in port_mac.get(i):
                port_mac[i] = j[2:][0:2] + ":" + j[2:][2:4] + ":" + j[2:][4:6] + ":" + j[2:][6:8] + ":" + j[2:][
                                                                                                          8:10] + ":" + j[
                                                                                                                        2:][
                                                                                                                        10:12]
        return port_mac

    def port_mac_switch_22():
        import pysnmp, re
        from pysnmp.entity.rfc3413.oneliner import cmdgen
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget(('172.16.5.22', 161)),
            '1.3.6.1.2.1.17.7.1.2.2.1.2',
            ignoreNonIncreasingOid=True)

        def mac(getvar):
            macs = getvar.split('.')
            i = 0
            ma = []
            for x in range(0, 6):
                maca = macs[i]
                if len(maca) == 1:
                    a = hex(int(maca)).replace("x", "")
                else:
                    a = hex(int(maca))[2:]
                ma.append(a)
                i = i + 1
            return ma[0] + ":" + ma[1] + ":" + ma[2] + ":" + ma[3] + ":" + ma[4] + ":" + ma[5]
        port_mac = []
        for i in varBinds:
            c = []
            for a, b in i:
                c.append(b.prettyPrint())
                c.append(mac(''.join(
                    re.findall(r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$', a.prettyPrint()))))
            port_mac.append(c)
        port_mac_dict = {}
        for j in range(1, 26):
            c = []
            for i in port_mac:
                if str(j) == i[0]:
                    c.append(i[1])
            if len(c) > 0:
                port_mac_dict[j] = c
        for i in [i for i in port_mac_dict.keys()]:
            if len(port_mac_dict.get(i)) <= 3:
                pass
            else:
                del port_mac_dict[i]
        return port_mac_dict

    def port_mac_switch_3():
        c = []
        for port in range(1, 52):
            errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(cmdgen.CommunityData('public'),
                cmdgen.UdpTransportTarget(('172.16.5.3', 161)),
                '1.3.6.1.4.1.11.2.14.11.5.1.9.4.2.1.2.' + str(port))
            port_mac_dict(port, varBinds)
        for i in [i for i in port_mac.keys()]:
            if len(port_mac.get(i)) <= 3:
                pass
            else:
                del port_mac[i]
        for i in [i for i in port_mac.keys()]:
            for j in port_mac.get(i):
                port_mac[i] = j[2:][0:2] + ":" + j[2:][2:4] + ":" + j[2:][4:6] + ":" + j[2:][6:8] + ":" + j[2:][
                                                                                                          8:10] + ":" + j[
                                                                                                                        2:][
                                                                                                                        10:12]
        return port_mac

    def port_mac_switch_11():
        c = []
        for port in range(1, 26):
            errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(cmdgen.CommunityData('public'),
                cmdgen.UdpTransportTarget(('172.16.5.11', 161)),
                '1.3.6.1.4.1.11.2.14.11.5.1.9.4.2.1.2.' + str(port))
            port_mac_dict(port, varBinds)
        for i in [i for i in port_mac.keys()]:
            if len(port_mac.get(i)) <= 3:
                pass
            else:
                del port_mac[i]
        for i in [i for i in port_mac.keys()]:
            for j in port_mac.get(i):
                port_mac[i] = j[2:][0:2] + ":" + j[2:][2:4] + ":" + j[2:][4:6] + ":" + j[2:][6:8] + ":" + j[2:][
                                                                                                          8:10] + ":" + j[
                                                                                                                        2:][
                                                                                                                        10:12]
        return port_mac

    def port_mac_switch_100():
        import pysnmp, re
        from pysnmp.entity.rfc3413.oneliner import cmdgen
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget(('172.16.5.100', 161)),
            '1.3.6.1.2.1.17.7.1.2.2.1.2',
            ignoreNonIncreasingOid=True)

        def mac(getvar):
            macs = getvar.split('.')
            i = 0
            ma = []
            for x in range(0, 6):
                maca = macs[i]
                if len(maca) == 1:
                    a = hex(int(maca)).replace("x", "")
                else:
                    a = hex(int(maca))[2:]
                ma.append(a)
                i = i + 1
            return ma[0] + ":" + ma[1] + ":" + ma[2] + ":" + ma[3] + ":" + ma[4] + ":" + ma[5]
        port_mac = []
        for i in varBinds:
            c = []
            for a, b in i:
                c.append(b.prettyPrint())
                c.append(mac(''.join(
                    re.findall(r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$', a.prettyPrint()))))
            port_mac.append(c)
        port_mac_dict = {}
        for j in range(1, 26):
            c = []
            for i in port_mac:
                if str(j) == i[0]:
                    c.append(i[1])
            if len(c) > 0:
                port_mac_dict[j] = c
        for i in [i for i in port_mac_dict.keys()]:
            if len(port_mac_dict.get(i)) <= 3:
                pass
            else:
                del port_mac_dict[i]
        return port_mac_dict

    def port_mac_switch_10():
        c = []
        for port in range(1, 52):
            errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(cmdgen.CommunityData('public'),
                                                                                cmdgen.UdpTransportTarget(
                                                                                    ('172.16.5.10', 161)),
                                                                                '1.3.6.1.4.1.11.2.14.11.5.1.9.4.2.1.2.' + str(
                                                                                    port))
            port_mac_dict(port, varBinds)
        for i in [i for i in port_mac.keys()]:
            if len(port_mac.get(i)) <= 3:
                pass
            else:
                del port_mac[i]
        for i in [i for i in port_mac.keys()]:
            for j in port_mac.get(i):
                port_mac[i] = j[2:][0:2] + ":" + j[2:][2:4] + ":" + j[2:][4:6] + ":" + j[2:][6:8] + ":" + j[2:][
                                                                                                          8:10] + ":" + j[
                                                                                                                        2:][
                                                                                                                        10:12]
        return port_mac


    def port_mac_switch_16():
        c = []
        for port in range(1, 52):
            errorIndication, errorStatus, errorIndex, varBinds = cmdGen.nextCmd(cmdgen.CommunityData('public'),
                                                                                cmdgen.UdpTransportTarget(
                                                                                    ('172.16.5.16', 161)),
                                                                                '1.3.6.1.4.1.11.2.14.11.5.1.9.4.2.1.2.' + str(
                                                                                    port))
            port_mac_dict(port, varBinds)
        for i in [i for i in port_mac.keys()]:
            if len(port_mac.get(i)) <= 3:
                pass
            else:
                del port_mac[i]
        for i in [i for i in port_mac.keys()]:
            for j in port_mac.get(i):
                port_mac[i] = j[2:][0:2] + ":" + j[2:][2:4] + ":" + j[2:][4:6] + ":" + j[2:][6:8] + ":" + j[2:][
                                                                                                          8:10] + ":" + j[
                                                                                                                        2:][
                                                                                                                        10:12]
        return port_mac


    all_ip_mac_dict = get_arp_all()[0]
    active_ip_mac_list = []
    for i in success:
        c = []
        c.append(i)
        c.append(all_ip_mac_dict.get(i))
        active_ip_mac_list.append(c)

    port_mac = port_mac_switch_4()
    list_keys = list(port_mac.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac[j]:
                i.append(j)
                i.append("sstc_805_2")

    port_mac_9 = port_mac_switch_9()
    list_keys = list(port_mac_9.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_9[j][0]:
                i.append(j)
                i.append("sstc_805_1")

    port_mac_13 = port_mac_switch_13()
    list_keys = list(port_mac_13.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_13[j]:
                i.append(j)
                i.append("sstc_705_1")

    port_mac_23 = port_mac_switch_23()
    list_keys = list(port_mac_23.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_23[j][0]:
                i.append(j)
                i.append("sstc_705_2")

    port_mac_8 = port_mac_switch_8()
    list_keys = list(port_mac_8.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_8[j][0]:
                i.append(j)
                i.append("sstc_605_1")

    port_mac_6 = port_mac_switch_6()
    list_keys = list(port_mac_6.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_6[j]:
                i.append(j)
                i.append("sstc_605_2")

    port_mac_15 = port_mac_switch_15()
    list_keys = list(port_mac_15.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_15[j]:
                i.append(j)
                i.append("sstc_505_1")

    port_mac_22 = port_mac_switch_22()
    list_keys = list(port_mac_22.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_22[j][0]:
                i.append(j)
                i.append("sstc_505_2")

    port_mac_3 = port_mac_switch_3()
    list_keys = list(port_mac_3.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_3[j]:
                i.append(j)
                i.append("sstc_505_3")

    port_mac_11 = port_mac_switch_11()
    list_keys = list(port_mac_11.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_11[j]:
                i.append(j)
                i.append("sstc_308_1")

    #print(port_mac_11)
    #print(active_ip_mac_list)

    port_mac_100 = port_mac_switch_100()
    list_keys = list(port_mac_100.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_100[j][0]:
                i.append(j)
                i.append("sstc_308_2")

    port_mac_10 = port_mac_switch_10()
    list_keys = list(port_mac_10.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_10[j]:
                i.append(j)
                i.append("405G")

    port_mac_16 = port_mac_switch_16()
    list_keys = list(port_mac_16.keys())
    for i in active_ip_mac_list:
        for j in list_keys:
            if i[-1] == port_mac_16[j]:
                i.append(j)
                i.append("405")


    nums = num(success)
    num = {}
    for i in nums:
        num[i] = active_ip_mac_list[i - 1]
    print(num)
    num_db = DiscoverData.objects.all().values()
    for i in range(1, len(DiscoverData.objects.values()) + 1):
        DiscoverData.objects.filter(num=i).delete()
#   DiscoverData.objects.all().delete()
    for i in range(1,len(num)):
        if len(num.get(i)) == 2:
            new_Disc = DiscoverData(num=i, ip=num.get(i)[0], mac= num.get(i)[1])
        else:
            new_Disc = DiscoverData(num=i, ip=num.get(i)[0], mac=num.get(i)[1], port=num.get(i)[2], switch=num.get(i)[3])
        new_Disc.save()
    return render(request, 'connections.html', {'num': num, 'num_db': num_db})
