#!/usr/bin/env python3

""" Modulos que se necesitan"""
import shodan
import dns.resolver
import argparse
import nmap
import io

SEPARATOR = "[+] {0} [+]".format('-' * 110)

""" Argumentos solicitados"""
def argumentos():
    parser = argparse.ArgumentParser()
    parser.add_argument("dominio",
                        type=str,
                        help='Digite el dominio que se analiza')
    args = parser.parse_args()
    return args


def dnsdata(dominio):
    ips = []
    """ Extraer los MX del dominio"""
    try:
        print(SEPARATOR)
        file(SEPARATOR)
        print("\t\t\tServicios de correo detectados \n")
        file("[+]\t\tServicios de correo detectados \n")
        for mx in dns.resolver.query(dominio, 'MX'):
            print('\t[!] ' + str(mx.exchange))
            file('\t[!] ' + str(mx.exchange))
    except:
        print("\t[*]  El dominio no tiene registros MX")
        file("\t[*]  El dominio no tiene registros MX")

    try:
        print("\n\n")
        print(SEPARATOR)
        file('\n' + SEPARATOR)
        print("\t\t\tRegistos de seguridad de correo\n")
        file("[+]\t\tRegistos de seguridad de correo\n")
        for txt in dns.resolver.query(dominio, 'TXT'):
            print('\t[!] ' + str(txt))
            file('\t[!] ' + str(txt))
    except:
        print("\n\t [*] No tiene registros de seguridad para correo")
        file("\t [*] No tiene registros de seguridad para correo")

    """ Extraer IPs """

    names = io.open("subdomains.txt", "r")
    #names=["", "www.", "mail.", "mail2", "correo", "webmail", "vpn", "hv"]
    for server in names:
        server = server.strip('\n\r')
        try:
            for ip in dns.resolver.query(server + "." + dominio, 'A'):
                ips.append(str(ip))
        except:
            pass
    return ips


def infonmap(ips):
    print('\n\n')
    print(SEPARATOR)
    file('\n' + SEPARATOR)
    print("\t\t\tInformación de las IPS \n")
    file("[+]\t\tInformación de las IPS \n")

    for ip in set(ips):
        nm = nmap.PortScanner()
        nm.scan(hosts=ip, arguments='-sV -T4 -Pn -p 21,22,23,25,80,81,82,123,443,445,993,1433,2222,3389,4443,8080,8443,27017')
        for port in nm[ip]['tcp'].keys():
            if nm[ip]['tcp'][port]['state'] == 'open':
                print('\t[*] Detectado un servicio en la IP ' + ip + ' en puerto ' + str(port))
                file('\t[*] Detectado un servicio en la IP ' + ip + ' en puerto ' + str(port))
                print('\t\t[!] Servicio : ' + nm[ip]['tcp'][port]['name'])
                file('\t\t[!] Servicio : ' + nm[ip]['tcp'][port]['name'])
                print('\t\t[!] Software : ' + nm[ip]['tcp'][port]['product'])
                file('\t\t[!] Software : ' + nm[ip]['tcp'][port]['product'])
                print('\t\t[!] Version : ' + nm[ip]['tcp'][port]['version'])
                file('\t\t[!] Version : ' + nm[ip]['tcp'][port]['version'])


def search_org(api_shodan, ips, args):
    """Lista de atributos que se resumiran por org"""
    FACETS = [
        ('port', 10),
        ('os', 10),
        ('vuln', 10),
        ('domain', 10),
        ('ssl.version', 10),
    ]

    FACET_TITLES = {
        'port': 'Top 10 Puertos',
        'os': 'Top 10 Operations Systems',
        'vuln': 'Top 10 Vulnerabilidades',
        'domain': 'Top 10 dominios',
        'ssl.version': 'Top 10 versiones SSL',
    }
    api = shodan.Shodan(api_shodan)
    for ip in ips:
        try:
            info = api.host(ip)
            if len(info['vulns']) >= 1:
                print("\n\n")
                print(SEPARATOR)
                file('\n' + SEPARATOR)
                print('\t\t\tDetectadas vulnerabilidad en la IP ' + ip)
                file('\t\t[+] Detectadas vulnerabilidad en la IP ' + ip)
                for vuln in info['vulns']:
                    print('\t\t[!] Vulnerabilidad : ' + vuln)
                    file('\t\t[!] Vulnerabilidad : ' + vuln)

        except Exception:
            continue

    try:

        args = args.split('.')[0]
        query = 'org:"' + args + '"'
        result = api.count(query, facets=FACETS)
        print("\n\n")
        print(SEPARATOR)
        file('\n' + SEPARATOR)
        print("\t\t\tRegistos de la organizacion   \n")
        file("[+]\t\tRegistos de la organizacion   \n")
        print('\t[!] Busqueda: %s' % query)
        file('\t[!] Busqueda: %s' % query)
        print('\t[!] Total detecciones: %s\n' % result['total'])
        file('\t[!] Total detecciones: %s\n' % result['total'])

        """Mostrar los resultados por facetas"""
        if result['total'] == 0:
            print('\t[*] El dominio no se detecta en ninguna organización')
            file('\t [*] El dominio no se detecta en ninguna organización')
        else:
            for facet in result['facets']:
                print('\t[*] ' + FACET_TITLES[facet])
                file('\t[*] ' + FACET_TITLES[facet])
                for term in result['facets'][facet]:
                    print('\t\t[!] %s: %s' % (term['value'], term['count']))
                    file('\t\t[!] %s: %s' % (term['value'], term['count']))

    except Exception as e:
        print('Error: %s' % e)


def file(dictname):
    files = open('report.txt', 'a')
    files.write(dictname)
    files.write('\n')
    files.close()


def main():
    """ Se configura la llave de la API de Shodan"""
    api_shodan = "PONER ACA LA APIKey"
    args = argumentos()
    if args.dominio is None:
        print(parser.print_usage)
        exit(0)
    else:
        ips = dnsdata(args.dominio)
        infonmap(ips)
        search_org(api_shodan, ips, args.dominio)


if __name__ == '__main__':
    main()
