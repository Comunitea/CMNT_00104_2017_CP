#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#sudo pip install feedparser

def main():
    """
    Metodo principal
    """
    PUERTOS_DICT = {
        '1': 'A Coruña',
        '2': 'Xixón',
        '3': 'Vigo',
        '4': 'Vilagarcía',
        '6': 'Ría de Foz',
        '7': 'Corcubión',
        '8': 'Ría de Camariñas',
        '9': 'Ría de Corme',
        '10': 'A Guarda',
        '11': 'Ribeira',
        '12': 'Muros',
        '13': 'Pontevedra',
        '14': 'Ferrol Porto Exterior',
        '15': 'Marín',
        '16': 'Ferrol'
    }

    import feedparser
    #rss='http://www.meteogalicia.gal/web/predicion/maritima/mareasIndex.action?request_locale=es&idPorto=1&data=26/04/2017'
    rss = 'http://servizos.meteogalicia.gal/rss/predicion/rssMareas.action?request_locale=es'
    parse_dict = feedparser.parse(rss)
    mareas_dict = {}
    #Por cada puerto tenemos que tener un diccionario con 2 horas distintas de Pleamar y 2 horas distintas de Bajamar
    for entry in parse_dict['entries']:
        #print "***%s****"%(entry['link'])
        url_link = entry['link']
        #La clave de mi diccionario sera el idPorto+data
        id_porto=url_link[url_link.find('idPorto')+8:url_link.find('data')-1]
        data = url_link[url_link.find('data')+5:]
        dict_key ="%s+%s"%(id_porto,data)
        port_dict = {}
        mareas_as_string = entry['summary']
        titulo_estado_mareas = mareas_as_string[mareas_as_string.find("<th>")+4:mareas_as_string.find("</th>")]
        #print "**%s"%(titulo_estado_mareas)
        mareas_as_string =mareas_as_string[mareas_as_string.find("</th>")+5:]
        titulo_hora_mareas = mareas_as_string[mareas_as_string.find("<th>")+4:mareas_as_string.find("</th>")]
        #print "**%s"%(titulo_hora_mareas)
        mareas_as_string =mareas_as_string[mareas_as_string.find("</th>")+5:]
        titulo_altura_mareas = mareas_as_string[mareas_as_string.find("<th>")+4:mareas_as_string.find("</th>")]
        #print "**%s"%(titulo_altura_mareas)

        mareas_as_string =mareas_as_string[mareas_as_string.find("</thead>")+8:]
        estado_mareas =  mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]
        if estado_mareas not in port_dict.keys():
            port_dict[estado_mareas] = []

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        hora_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        altura_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]


        port_dict[estado_mareas] = [(hora_mareas,altura_mareas)]

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        estado_2_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        hora_2_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        altura_2_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]

        if estado_2_mareas not in port_dict.keys():
            port_dict[estado_2_mareas] = [(hora_2_mareas,altura_2_mareas)]
        else:
            port_dict[estado_2_mareas].append((hora_2_mareas,altura_2_mareas))

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        estado_3_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        hora_3_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        altura_3_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]

        if estado_3_mareas not in port_dict.keys():
            port_dict[estado_3_mareas] = [(hora_3_mareas,altura_3_mareas)]
        else:
            port_dict[estado_3_mareas].append((hora_3_mareas,altura_3_mareas))

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        estado_4_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        hora_4_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]

        mareas_as_string =mareas_as_string[mareas_as_string.find("</td>")+5:]
        altura_4_mareas = mareas_as_string[mareas_as_string.find("<td>")+4:mareas_as_string.find("</td>")]

        if estado_4_mareas not in port_dict.keys():
            port_dict[estado_4_mareas] = [(hora_4_mareas,altura_4_mareas)]
        else:
            port_dict[estado_4_mareas].append((hora_4_mareas,altura_4_mareas))

        mareas_dict[dict_key] = port_dict
    return mareas_dict

if __name__ == "__main__":
    main()
