#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os

OUT = "/home/igor/cursorwork/sustatov/opencode/people"
os.makedirs(OUT, exist_ok=True)

P = {}  # id -> dict

def add(d):
    P[d["id"]] = d

SRC = {
 "vgd": {"type": "forum", "ref": "https://forum.vgd.ru/2339/86148/"},
 "vgd20": {"type": "forum", "ref": "https://forum.vgd.ru/2339/86148/20.htm"},
 "vgd100": {"type": "forum", "ref": "https://forum.vgd.ru/2339/86148/100.htm"},
 "vgd110": {"type": "forum", "ref": "https://forum.vgd.ru/2339/86148/110.htm"},
 "vgd140": {"type": "forum", "ref": "https://forum.vgd.ru/2339/86148/140.htm"},
 "vgd160": {"type": "forum", "ref": "https://forum.vgd.ru/2339/86148/160.htm"},
 "vgd170": {"type": "forum", "ref": "https://forum.vgd.ru/2339/86148/170.htm"},
 "vgd230": {"type": "forum", "ref": "https://forum.vgd.ru/2339/86148/230.htm"},
 "vgd270": {"type": "forum", "ref": "https://forum.vgd.ru/2339/86148/270.htm"},
 "vgd290": {"type": "forum", "ref": "https://forum.vgd.ru/2339/86148/290.htm"},
 "sarpust1": {"type": "url", "ref": "http://sarpust.ru/2015/02/vospominaniya-n-g-sustatova-chast-i-koshelihinskij-spirtzavod/"},
 "sarpust3": {"type": "url", "ref": "http://sarpust.ru/2015/02/vospominaniya-n-g-sustatova-chast-iii-dezertiry-i-gul-komovtsy/"},
 "pamnar": {"type": "url", "ref": "https://pamyat-naroda.ru/heroes/isp-chelovek_spisok2324860/"},
 "vostlit1671": {"type": "url", "ref": "https://vostlit.info/Texts/Dokumenty/Russ/XVII/1660-1680/Perep_kniga_alatyr_1671/text1.htm"},
 "veselovsky": {"type": "book", "ref": "Веселовский С.Б. Арзамасские поместные акты (1578–1618). М., 1915"},
 "demidov": {"type": "article", "ref": "Демидов А.Н. «Еделевский» список… 1572 г. Финно-угорский мир, т.12 №1, 2020"},
 "rgada": {"type": "archive", "ref": "РГАДА, ф.350, оп.2, д.114, лл.1262–1267"},
 "cano60": {"type": "archive", "ref": "ЦАНО, ф.60, оп.239А, д.463, 599"},
 "cano570": {"type": "archive", "ref": "ЦАНО, ф.570, оп.10, д.142–148"},
 "gedcom": {"type": "file", "ref": "MyHeritage GEDCOM"},
}

# ===== XVII век (контекст) =====
add({"id":"X01","surname":"Сустатов","given_name":"Сыресь","patronymic":"","full_name":"Сыресь Сустатов","sex":"M",
"birth":{"date":"","place":"Арзамасский уезд"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"xvii","generation":0,"relation_to_direct_line":"родоначальник арзамасско-нижегородской ветви (связь с прямой линией не доказана)",
"social_estate":"мурза (мордовский князь)","occupation":"","religion":"дохристианская мордва (эрзя)","notes":"«еделевский мурза»; упом. 1596 и 1603; родовое «знамя» (бортная тамга) изображено в акте 1596",
"relationships":{"father":None,"mother":None,"spouses":[],"children":[]},
"sources":[SRC["veselovsky"],SRC["demidov"]],"events":[{"type":"mention","date":"1596","note":"акт №100 — Сыресь Сустатов с «знаменем»"},{"type":"mention","date":"1603","note":"акт №177"}]})

add({"id":"X02","surname":"Сустатов","given_name":"Сустат","patronymic":"Канесев сын","full_name":"Сустат Канесев сын","sex":"M",
"birth":{"date":"","place":"Нижегородский уезд"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"xvii","generation":0,"relation_to_direct_line":"однофамилец XVI в. (не установлено родство)",
"social_estate":"ясачная мордва","occupation":"","religion":"дохристианская мордва","notes":"1591 — «мордва Сустатъ Канесевъ сынъ… знамя свое приложилъ»",
"relationships":{"father":None,"mother":None,"spouses":[],"children":[]},
"sources":[SRC["veselovsky"]],"events":[{"type":"mention","date":"1591","note":"акт №47"}]})

add({"id":"X03","surname":"Сустатов","given_name":"Ненашка","patronymic":"","full_name":"Ненашка Сустатов","sex":"M",
"birth":{"date":"","place":"д. Хмелевка, Алатырский уезд"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"xvii","generation":0,"relation_to_direct_line":"боковая (Алатырский уезд, 1671)",
"social_estate":"ясачная мордва","occupation":"бортник","religion":"дохристианская мордва","notes":"переписная книга 1671",
"relationships":{"father":None,"mother":None,"spouses":[],"children":[]},
"sources":[SRC["vostlit1671"]],"events":[{"type":"mention","date":"1671","note":"жилой двор, д. Хмелевка"}]})

add({"id":"X04","surname":"Сустатов","given_name":"Исанка","patronymic":"","full_name":"Исанка Сустатов","sex":"M",
"birth":{"date":"","place":"д. Хмелевка, Алатырский уезд"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"xvii","generation":0,"relation_to_direct_line":"боковая (Алатырский уезд, 1671)",
"social_estate":"ясачная мордва","occupation":"","religion":"дохристианская мордва","notes":"переписная книга 1671; сын Алешка",
"relationships":{"father":None,"mother":None,"spouses":[],"children":["X05"]},
"sources":[SRC["vostlit1671"]],"events":[{"type":"mention","date":"1671","note":"жилой двор, д. Хмелевка"}]})

add({"id":"X05","surname":"Сустатов","given_name":"Алешка","patronymic":"","full_name":"Алешка (сын Исанки Сустатова)","sex":"M",
"birth":{"date":"","place":"д. Хмелевка, Алатырский уезд"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"xvii","generation":0,"relation_to_direct_line":"боковая (1671)",
"social_estate":"ясачная мордва","occupation":"","religion":"","notes":"сын Исанки Сустатова",
"relationships":{"father":"X04","mother":None,"spouses":[],"children":[]},
"sources":[SRC["vostlit1671"]],"events":[{"type":"mention","date":"1671","note":""}]})

add({"id":"X06","surname":"Сустатов","given_name":"Ездайка","patronymic":"","full_name":"Ездайка Сустатов","sex":"M",
"birth":{"date":"","place":"д. Сыресева, Алатырский уезд"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"xvii","generation":0,"relation_to_direct_line":"житель д. Сыресевой (1671) — возможная связь с происхождением прямой линии",
"social_estate":"ясачная мордва","occupation":"","religion":"дохристианская мордва","notes":"переписная книга 1671, д. Сыресева",
"relationships":{"father":None,"mother":None,"spouses":[],"children":[]},
"sources":[SRC["vostlit1671"]],"events":[{"type":"mention","date":"1671","note":"жилой двор, д. Сыресева"}]})

add({"id":"X07","surname":"Сустатов","given_name":"Итяска","patronymic":"","full_name":"Итяска Сустатов","sex":"M",
"birth":{"date":"","place":"д. Баева, Алатырский уезд"},"death":{"date":"1670","place":"Кондарать","cause":"убит (восстание Разина)"},
"status":"CONFIRMED","category":"xvii","generation":0,"relation_to_direct_line":"боковая (1671)",
"social_estate":"ясачная мордва","occupation":"","religion":"","notes":"«дв. пуст Итяски Сустатова, убит на Кондарате»",
"relationships":{"father":None,"mother":None,"spouses":[],"children":[]},
"sources":[SRC["vostlit1671"]],"events":[{"type":"death","date":"1670","note":"убит на Кондарати"}]})

add({"id":"X08","surname":"Сыресев (Еделев)","given_name":"Бажен","patronymic":"Чепкунов сын","full_name":"Бажен Чепкунов сын Сыресев","sex":"M",
"birth":{"date":"","place":""},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"xvii","generation":0,"relation_to_direct_line":"князья Еделевы (отделившаяся ветвь рода)",
"social_estate":"мурза","occupation":"","religion":"","notes":"племянник Девая Сыресева; владел 14 дворами в д. Еделево",
"relationships":{"father":None,"mother":None,"spouses":[],"children":[]},
"sources":[SRC["demidov"]],"events":[]})

add({"id":"X09","surname":"Еделев","given_name":"Мамкай (Мамлей)","patronymic":"Ногаев сын","full_name":"Мамкай (Мамлей) мурза Ногаев","sex":"M",
"birth":{"date":"","place":""},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"xvii","generation":0,"relation_to_direct_line":"князья Еделевы",
"social_estate":"мурза","occupation":"","religion":"","notes":"Смотренный список 1643 — 200 четей, 11 дворов",
"relationships":{"father":None,"mother":None,"spouses":[],"children":[]},
"sources":[SRC["demidov"]],"events":[{"type":"mention","date":"1643","note":"Смотренный список служилых татар Алатырского уезда"}]})

add({"id":"X10","surname":"Еделев","given_name":"Надежа","patronymic":"Суморев сын","full_name":"Надежа мурза Суморев","sex":"M",
"birth":{"date":"","place":""},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"xvii","generation":0,"relation_to_direct_line":"князья Еделевы",
"social_estate":"мурза","occupation":"","religion":"","notes":"Смотренный список 1643 — 250 четей, 2 двора",
"relationships":{"father":None,"mother":None,"spouses":[],"children":[]},
"sources":[SRC["demidov"]],"events":[{"type":"mention","date":"1643","note":""}]})

# ===== Прямая линия =====
add({"id":"D03","surname":"Сустатов","given_name":"Никита","patronymic":"Иванович","full_name":"Никита Иванович Сустатов","sex":"M",
"birth":{"date":"~1715–1719","place":"дворцовая деревня Сыресева"},"death":{"date":"1773","place":"","cause":""},
"status":"CONFIRMED","category":"direct","generation":1,"relation_to_direct_line":"прямой предок",
"social_estate":"ясачная/дворцовая мордва","occupation":"","religion":"новокрещён","notes":"ревизии 1748 (29 л., «прибывшие из дворцовой д. Сыресевой»), 1763 (47/48), †1773 (по ревизии 1782)",
"relationships":{"father":None,"mother":None,"spouses":["SP01"],"children":["D04","S13"]},
"sources":[SRC["rgada"]],"events":[{"type":"migration","date":"~1724","note":"переселение из д. Сыресевой в Камкину (Кошелиху)"}]})

add({"id":"D04","surname":"Сустатов","given_name":"Пётр","patronymic":"Никитич","full_name":"Пётр Никитич Сустатов","sex":"M",
"birth":{"date":"~1737","place":"с. Кошелиха (Камкина)"},"death":{"date":"1819","place":"","cause":""},
"status":"CONFIRMED","category":"direct","generation":2,"relation_to_direct_line":"прямой предок",
"social_estate":"государственный крестьянин","occupation":"","religion":"православие","notes":"ревизии 1763 (26/27), 1782; †1819 (зафиксировано ревизией 1834)",
"relationships":{"father":"D03","mother":"SP01","spouses":["SP02"],"children":["D05","S14"]},
"sources":[SRC["cano60"]],"events":[]})

add({"id":"D05","surname":"Сустатов","given_name":"Андрей","patronymic":"Петрович","full_name":"Андрей Петрович Сустатов","sex":"M",
"birth":{"date":"~1760","place":"с. Кошелиха (Камкина), Ардатовский уезд"},"death":{"date":"1811","place":"","cause":""},
"status":"CONFIRMED","category":"direct","generation":3,"relation_to_direct_line":"прямой предок",
"social_estate":"государственный крестьянин","occupation":"","religion":"православие","notes":"ревизия 1811 (50 лет); жена Дарья; дети Лев, Иван, Кондратий, Василий",
"relationships":{"father":"D04","mother":"SP02","spouses":["SP03"],"children":["D06","S01","S02","S03"]},
"sources":[SRC["cano60"]],"events":[]})

add({"id":"D06","surname":"Сустатов","given_name":"Иван","patronymic":"Андреевич","full_name":"Иван Андреевич Сустатов","sex":"M",
"birth":{"date":"~1793","place":"с. Кошелиха"},"death":{"date":"1833","place":"","cause":""},
"status":"CONFIRMED","category":"direct","generation":4,"relation_to_direct_line":"прямой предок",
"social_estate":"государственный крестьянин","occupation":"","religion":"православие","notes":"ревизия 1811 (18 л.), «достался по разделу с сёстрами в 1812»; †1833; жена Мавра",
"relationships":{"father":"D05","mother":"SP03","spouses":["SP04"],"children":["D07"]},
"sources":[SRC["cano60"]],"events":[]})

add({"id":"D07","surname":"Сустатов","given_name":"Иван","patronymic":"Иванович","full_name":"Иван Иванович Сустатов","sex":"M",
"birth":{"date":"~1815","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"direct","generation":5,"relation_to_direct_line":"прямой предок",
"social_estate":"государственный крестьянин","occupation":"","religion":"православие","notes":"ревизия 1858 (36/43); жена Матрёна Фёдоровна; сыновья Фёдор, Федот, Иван(1847), Иван(1851)",
"relationships":{"father":"D06","mother":"SP04","spouses":["SP05"],"children":["D08","S04","S05"]},
"sources":[SRC["cano60"]],"events":[]})

add({"id":"D08","surname":"Сустатов","given_name":"Иван","patronymic":"Иванович","full_name":"Иван Иванович Сустатов","sex":"M",
"birth":{"date":"~1847","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"direct","generation":6,"relation_to_direct_line":"прямой предок",
"social_estate":"государственный крестьянин","occupation":"","religion":"православие","notes":"сын Ивана Ивановича (~1815) по ревизии 1858; ⚠️ разграничить от тёзки-брата Ивана (~1851)",
"relationships":{"father":"D07","mother":"SP05","spouses":[],"children":["D09"]},
"sources":[SRC["cano60"]],"events":[]})

add({"id":"D09","surname":"Сустатов","given_name":"Иван","patronymic":"Иванович","full_name":"Иван Иванович Сустатов","sex":"M",
"birth":{"date":"~1870","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"PROBABLE","category":"direct","generation":7,"relation_to_direct_line":"отец Василия Ивановича (по отчеству «Иванович»)",
"social_estate":"крестьянин","occupation":"","religion":"православие","notes":"недостающее звено; подтвердить метрикой",
"relationships":{"father":"D08","mother":None,"spouses":[],"children":["D10"]},
"sources":[SRC["cano570"]],"events":[]})

add({"id":"D10","surname":"Сустатов","given_name":"Василий","patronymic":"Иванович","full_name":"Василий Иванович Сустатов","sex":"M",
"birth":{"date":"~1890","place":"с. Кошелиха, Ардатовский уезд"},"death":{"date":"1934","place":"","cause":""},
"status":"CONFIRMED","category":"direct","generation":8,"relation_to_direct_line":"прямой предок",
"social_estate":"крестьянин","occupation":"","religion":"православие","notes":"брак 30.06.1908 (17½ л.) с Прасковьей Королёвой; ПМВ рядовой 3-го Заамурского полка, ранен 15.06.1916",
"relationships":{"father":"D09","mother":None,"spouses":["SP06"],"children":["D11","S06","S07"]},
"sources":[SRC["cano570"],SRC["vgd100"]],"events":[{"type":"marriage","date":"30.06.1908","note":"с Прасковьей Фёдоровной Королёвой"},{"type":"military","date":"1916","note":"ранен, 3-й Заамурский пограничный полк"}]})

add({"id":"D11","surname":"Сустатов","given_name":"Григорий","patronymic":"Васильевич","full_name":"Григорий Васильевич Сустатов","sex":"M",
"birth":{"date":"19.01.1912","place":"с. Кошелиха, Горьковская обл."},"death":{"date":"10.03.1942","place":"с. Приколотное, Харьковская обл.","cause":"умер от ран (ВОВ)"},
"status":"CONFIRMED","category":"direct","generation":9,"relation_to_direct_line":"прямой предок",
"social_estate":"крестьянин","occupation":"столяр","religion":"православие","notes":"987 сп 226 сд, пулемётчик/санитар, вынес 40 раненых; подорвался на мине 07.03.1942; похоронен в братской могиле",
"relationships":{"father":"D10","mother":"SP06","spouses":["SP07"],"children":["D12","S08","S09","S10","S11"]},
"sources":[SRC["pamnar"],SRC["vgd20"]],"events":[{"type":"military","date":"1941","note":"призван из колхоза «Красный Октябрь»"},{"type":"death","date":"10.03.1942","note":"умер от ран в госпитале"}]})

add({"id":"D12","surname":"Сустатов","given_name":"Василий","patronymic":"Григорьевич","full_name":"Василий Григорьевич Сустатов","sex":"M",
"birth":{"date":"24.01.1930","place":"с. Кошелиха, Первомайский р-н, Горьковская обл."},"death":{"date":"06.10.2004","place":"г. Калининград","cause":""},
"status":"CONFIRMED","category":"direct","generation":10,"relation_to_direct_line":"прямой предок",
"social_estate":"","occupation":"","religion":"","notes":"прозвище «Кошка» (гулькомовцы); жена Александра Ковригина",
"relationships":{"father":"D11","mother":"SP07","spouses":["SP08"],"children":["D13","S12"]},
"sources":[SRC["gedcom"],SRC["sarpust3"]],"events":[]})

add({"id":"D13","surname":"Сустатов","given_name":"Григорий","patronymic":"Васильевич","full_name":"Григорий Васильевич Сустатов","sex":"M",
"birth":{"date":"30.08.1954","place":""},"death":{"date":"24.12.2020","place":"г. Калининград","cause":"COVID-19"},
"status":"CONFIRMED","category":"direct","generation":11,"relation_to_direct_line":"прямая линия",
"social_estate":"","occupation":"","religion":"","notes":"похоронен: военно-мемориальное кладбище «Курган Славы»; жёны Ольга Сальникова, Людмила Эдуардовна",
"relationships":{"father":"D12","mother":"SP08","spouses":["SP09","SP10"],"children":["D14"]},
"sources":[SRC["gedcom"]],"events":[]})

add({"id":"D14","surname":"Сальников","given_name":"Игорь","patronymic":"","full_name":"Игорь Сальников","sex":"M",
"birth":{"date":"16.12.1982","place":"г. Ленинград"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"direct","generation":12,"relation_to_direct_line":"сын Григория 1954",
"social_estate":"","occupation":"","religion":"","notes":"автор GEDCOM; фамилия по матери Ольге Сальниковой",
"relationships":{"father":"D13","mother":"SP09","spouses":[],"children":[]},
"sources":[SRC["gedcom"]],"events":[]})

# ===== Братья/сёстры прямой линии =====
add({"id":"S13","surname":"Сустатова","given_name":"Федосья","patronymic":"Никитична","full_name":"Федосья Никитична","sex":"F",
"birth":{"date":"~1753","place":""},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":2,"relation_to_direct_line":"сестра Петра Никитича (дочь Никиты)",
"social_estate":"","occupation":"","religion":"","notes":"дочь Никиты Ивановича (ревизия 1763, 10 л.)",
"relationships":{"father":"D03","mother":"SP01","spouses":[],"children":[]},
"sources":[SRC["rgada"]],"events":[]})

add({"id":"S14","surname":"Сустатов","given_name":"Михаил","patronymic":"Петрович","full_name":"Михаил Петрович Сустатов","sex":"M",
"birth":{"date":"~1752","place":""},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":3,"relation_to_direct_line":"брат Андрея Петровича",
"social_estate":"","occupation":"","religion":"","notes":"сын Петра Никитича (ревизия 1763, 11 л.)",
"relationships":{"father":"D04","mother":"SP02","spouses":[],"children":[]},
"sources":[SRC["rgada"]],"events":[]})

add({"id":"S01","surname":"Сустатов","given_name":"Лев","patronymic":"Андреевич","full_name":"Лев Андреевич Сустатов","sex":"M",
"birth":{"date":"","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":4,"relation_to_direct_line":"брат Ивана Андреевича",
"social_estate":"государственный крестьянин","occupation":"","religion":"","notes":"ревизии 1851/1858 (52/69, 69/76); жена Варвара Васильевна",
"relationships":{"father":"D05","mother":"SP03","spouses":[],"children":[]},
"sources":[SRC["vgd140"]],"events":[]})

add({"id":"S02","surname":"Сустатов","given_name":"Кондратий","patronymic":"Андреевич","full_name":"Кондратий Андреевич Сустатов","sex":"M",
"birth":{"date":"","place":"с. Кошелиха"},"death":{"date":"1847","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":4,"relation_to_direct_line":"брат Ивана Андреевича",
"social_estate":"государственный крестьянин","occupation":"","religion":"","notes":"брак 08.11.1807; жена Анна Филипповна; ревизия 1851 «42 / умер 1847»",
"relationships":{"father":"D05","mother":"SP03","spouses":["SP13"],"children":["C01"]},
"sources":[SRC["vgd140"],SRC["vgd160"]],"events":[{"type":"marriage","date":"08.11.1807","note":"сын Андрея Петровича"}]})

add({"id":"S03","surname":"Сустатов","given_name":"Василий","patronymic":"Андреевич","full_name":"Василий Андреевич Сустатов","sex":"M",
"birth":{"date":"~1817","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":4,"relation_to_direct_line":"брат Ивана Андреевича",
"social_estate":"государственный крестьянин","occupation":"","religion":"","notes":"ревизия 1858 (58/65); сын Аким",
"relationships":{"father":"D05","mother":"SP03","spouses":[],"children":["C02"]},
"sources":[SRC["vgd140"]],"events":[]})

add({"id":"S04","surname":"Сустатов","given_name":"Фёдор","patronymic":"Иванович","full_name":"Фёдор Иванович Сустатов","sex":"M",
"birth":{"date":"~1842","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":6,"relation_to_direct_line":"брат Ивана Ивановича (~1847)",
"social_estate":"государственный крестьянин","occupation":"","religion":"","notes":"сын Ивана Ивановича (~1815), ревизия 1858",
"relationships":{"father":"D07","mother":"SP05","spouses":[],"children":["C03"]},
"sources":[SRC["cano60"],SRC["vgd140"]],"events":[]})

add({"id":"S05","surname":"Сустатов","given_name":"Федот","patronymic":"Иванович","full_name":"Федот Иванович Сустатов","sex":"M",
"birth":{"date":"","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":6,"relation_to_direct_line":"брат Ивана Ивановича (~1847)",
"social_estate":"государственный крестьянин","occupation":"","religion":"","notes":"сын Ивана Ивановича (~1815), ревизия 1858",
"relationships":{"father":"D07","mother":"SP05","spouses":[],"children":["C05"]},
"sources":[SRC["cano60"]],"events":[]})

add({"id":"S06","surname":"Сустатов","given_name":"Алексей","patronymic":"Васильевич","full_name":"Алексей Васильевич Сустатов","sex":"M",
"birth":{"date":"1913","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":9,"relation_to_direct_line":"брат Григория 1912",
"social_estate":"","occupation":"","religion":"","notes":"рядовой; прибыл 20.09.1944 на Горьковский ВПП, убыл 03.10.1944 п/п 55390 г. Муром",
"relationships":{"father":"D10","mother":"SP06","spouses":[],"children":[]},
"sources":[SRC["vgd170"]],"events":[{"type":"military","date":"1944","note":"ВПП"}]})

add({"id":"S07","surname":"Сустатов","given_name":"Максим","patronymic":"Васильевич","full_name":"Максим Васильевич Сустатов","sex":"M",
"birth":{"date":"1917","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":9,"relation_to_direct_line":"брат Григория 1912",
"social_estate":"","occupation":"","religion":"","notes":"рядовой; ВПП 1943–1944; орден Отечественной войны II (1985)",
"relationships":{"father":"D10","mother":"SP06","spouses":[],"children":[]},
"sources":[SRC["vgd170"],SRC["vgd20"]],"events":[{"type":"military","date":"1943–1944","note":"ВПП"}]})

add({"id":"S08","surname":"Сустатова","given_name":"Татьяна","patronymic":"","full_name":"Татьяна Сустатова","sex":"F",
"birth":{"date":"1932","place":""},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":10,"relation_to_direct_line":"сестра Василия 1930",
"social_estate":"","occupation":"","religion":"","notes":"дочь Григория 1912",
"relationships":{"father":"D11","mother":"SP07","spouses":[],"children":[]},
"sources":[SRC["gedcom"]],"events":[]})

add({"id":"S09","surname":"Сустатова","given_name":"Анна","patronymic":"","full_name":"Анна Сустатова","sex":"F",
"birth":{"date":"10.07.1934","place":""},"death":{"date":"23.08.1953","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":10,"relation_to_direct_line":"сестра Василия 1930",
"social_estate":"","occupation":"","religion":"","notes":"дочь Григория 1912; умерла в 19 лет",
"relationships":{"father":"D11","mother":"SP07","spouses":[],"children":[]},
"sources":[SRC["gedcom"]],"events":[]})

add({"id":"S10","surname":"Сустатов","given_name":"Николай","patronymic":"Григорьевич","full_name":"Николай Григорьевич Сустатов","sex":"M",
"birth":{"date":"04.10.1936","place":"с. Кошелиха, Первомайский р-н, Горьковская обл."},"death":{"date":"29.10.2018","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":10,"relation_to_direct_line":"брат Василия 1930",
"social_estate":"","occupation":"мемуарист; ВНИИЭФ","religion":"","notes":"автор воспоминаний о Кошелихе; служил на флоте 1955-59; жена Нина",
"relationships":{"father":"D11","mother":"SP07","spouses":["SP12"],"children":[]},
"sources":[SRC["sarpust1"],SRC["gedcom"]],"events":[]})

add({"id":"S11","surname":"Сустатова","given_name":"Вера","patronymic":"","full_name":"Вера Сустатова","sex":"F",
"birth":{"date":"07.10.1939","place":""},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":10,"relation_to_direct_line":"сестра Василия 1930",
"social_estate":"","occupation":"","religion":"","notes":"дочь Григория 1912",
"relationships":{"father":"D11","mother":"SP07","spouses":[],"children":[]},
"sources":[SRC["gedcom"]],"events":[]})

add({"id":"S12","surname":"Сустатова","given_name":"Елена","patronymic":"","full_name":"Елена Сустатова (Ермолина)","sex":"F",
"birth":{"date":"01.06.1959","place":""},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"sibling","generation":11,"relation_to_direct_line":"сестра Григория 1954",
"social_estate":"","occupation":"","religion":"","notes":"муж Дмитрий Ермолин; дети Никита (1982), Дарья (1987)",
"relationships":{"father":"D12","mother":"SP08","spouses":["SP11"],"children":[]},
"sources":[SRC["gedcom"]],"events":[]})

# ===== Двоюродные / потомки братьев =====
add({"id":"C01","surname":"Сустатов","given_name":"Аверьян","patronymic":"Кондратьевич","full_name":"Аверьян Кондратьевич Сустатов","sex":"M",
"birth":{"date":"~1827","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"cousin","generation":5,"relation_to_direct_line":"двоюродный (сын Кондратия Андреевича)",
"social_estate":"","occupation":"","religion":"","notes":"ревизия 1858 (31/38); жена Дарья Анисимовна",
"relationships":{"father":"S02","mother":"SP13","spouses":[],"children":[]},
"sources":[SRC["vgd140"]],"events":[]})

add({"id":"C02","surname":"Сустатов","given_name":"Аким","patronymic":"Васильевич","full_name":"Аким Васильевич Сустатов","sex":"M",
"birth":{"date":"","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"cousin","generation":5,"relation_to_direct_line":"двоюродный (сын Василия Андреевича)",
"social_estate":"","occupation":"","religion":"","notes":"ревизия 1858 (38/45)",
"relationships":{"father":"S03","mother":None,"spouses":[],"children":[]},
"sources":[SRC["vgd140"]],"events":[]})

add({"id":"C03","surname":"Сустатов","given_name":"Александр","patronymic":"Фёдорович","full_name":"Александр Фёдорович Сустатов","sex":"M",
"birth":{"date":"~1870","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"cousin","generation":7,"relation_to_direct_line":"двоюродный (сын Фёдора Ивановича)",
"social_estate":"","occupation":"","religion":"","notes":"брак 09.11.1890; жена Екатерина",
"relationships":{"father":"S04","mother":None,"spouses":[],"children":["C04"]},
"sources":[SRC["vgd160"]],"events":[{"type":"marriage","date":"09.11.1890","note":"сын Фёдора Ивановича"}]})

add({"id":"C04","surname":"Сустатов","given_name":"Серафим","patronymic":"Александрович","full_name":"Серафим Александрович Сустатов","sex":"M",
"birth":{"date":"1909","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"cousin","generation":8,"relation_to_direct_line":"троюродный (сын Александра Фёдоровича)",
"social_estate":"","occupation":"","religion":"","notes":"рядовой 393 опаб 154 УР; орден Отечественной войны II (07.05.1944)",
"relationships":{"father":"C03","mother":None,"spouses":[],"children":[]},
"sources":[SRC["vgd20"],SRC["vgd170"]],"events":[{"type":"military","date":"1941–1944","note":"в армии с 04.10.1941, трижды ранен"}]})

add({"id":"C05","surname":"Сустатов","given_name":"Алексей","patronymic":"Федотович","full_name":"Алексей Федотович Сустатов","sex":"M",
"birth":{"date":"~1874","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"cousin","generation":7,"relation_to_direct_line":"двоюродный (сын Федота Ивановича)",
"social_estate":"","occupation":"","religion":"","notes":"брак 19.04.1892 с Евфросинией; ПМВ 1917",
"relationships":{"father":"S05","mother":None,"spouses":[],"children":[]},
"sources":[SRC["vgd160"]],"events":[{"type":"marriage","date":"19.04.1892","note":""}]})

# ===== Боковые ветви (ВОВ и др., родство с прямой линией не установлено) =====
def collateral(id,surname,given,patronymic,full,dates,note,src):
    add({"id":id,"surname":surname,"given_name":given,"patronymic":patronymic,"full_name":full,"sex":"M",
    "birth":{"date":dates[0],"place":"с. Кошелиха"},"death":{"date":dates[1] if len(dates)>1 else "","place":"","cause":""},
    "status":"CONFIRMED","category":"collateral","generation":0,"relation_to_direct_line":"боковая ветвь (родство не установлено)",
    "social_estate":"","occupation":"","religion":"","notes":note,
    "relationships":{"father":None,"mother":None,"spouses":[],"children":[]},
    "sources":[SRC[src]],"events":[]})

collateral("C06","Сустатов","Василий","Яковлевич","Василий Яковлевич Сустатов",["1910/16.02.1911","09.12.1941"],"попал в плен 18.07.1941 в Кричеве; погиб в плену (шталаг IV B)","vgd20")
collateral("C07","Сустатов","Николай","Яковлевич","Николай Яковлевич Сустатов",["1918","20.12.1943"],"красноармеец 257 сд 948 сп; погиб","vgd20")
collateral("C08","Сустатов","Степан","Фёдорович","Степан Фёдорович Сустатов",["1910","01.05.1943"],"вступил в партизанский отряд 11.01.1943; погиб","vgd20")
collateral("C09","Сустатов","Яков","Фёдорович","Яков Фёдорович Сустатов",["12.02.1910","08.05.1942"],"сержант; попал в плен 28.08.1941; погиб в плену","vgd20")
collateral("C10","Сустатов","Михаил","Фёдорович","Михаил Фёдорович Сустатов",["1913",""],"пропал без вести __.12.1941","vgd20")
collateral("C11","Сустатов","Алексей","Фёдорович","Алексей Фёдорович Сустатов",["1918",""],"старшина 854 сп 277 сд; награды: «За боевые заслуги», 2×Отеч.войны II, 2×Красная Звезда, Слава III","vgd100")
collateral("C12","Сустатов","Григорий","Михайлович","Григорий Михайлович Сустатов",["1918",""],"рядовой 110 тбр 18 тк; «За боевые заслуги», Отеч.войны II","vgd100")
collateral("C13","Сустатов","Николай","Иванович","Николай Иванович Сустатов",["1915",""],"ст. сержант; медаль «За боевые заслуги» (22.08.1944)","vgd100")
collateral("C14","Сустатов","Борис","Семёнович","Борис Семёнович Сустатов",["1908","20.03.1938"],"прораб; арестован 13.01.1938, расстрелян (Бутово), реабилитирован 1959","vgd20")
collateral("C15","Сустатов","Борис","Михайлович","Борис Михайлович Сустатов",["",""],"рекрут с 1805 г. (ревизии 1811/1816)","vgd110")

# ===== Супруги =====
def spouse(id,surname,given,patronymic,full,sex,dates,husband_wife,note,src):
    add({"id":id,"surname":surname,"given_name":given,"patronymic":patronymic,"full_name":full,"sex":sex,
    "birth":{"date":dates[0],"place":""},"death":{"date":dates[1] if len(dates)>1 else "","place":"","cause":""},
    "status":"CONFIRMED","category":"spouse","generation":0,"relation_to_direct_line":"супруг(а) по браку",
    "social_estate":"","occupation":"","religion":"","notes":note,
    "relationships":{"father":None,"mother":None,"spouses":[husband_wife],"children":[]},
    "sources":[SRC[src]],"events":[]})

spouse("SP01","","Авдотья","Васильевна","Авдотья Васильевна","F",["~1715",""],"D03","жена Никиты Ивановича","rgada")
spouse("SP02","","Аксинья","Алексеевна","Аксинья Алексеевна (Ивановна)","F",["~1740",""],"D04","жена Петра Никитича","rgada")
spouse("SP03","","Дарья","","Дарья","F",["",""],"D05","жена Андрея Петровича","cano60")
spouse("SP04","","Мавра","","Мавра","F",["",""],"D06","жена Ивана Андреевича","cano60")
spouse("SP05","","Матрёна","Фёдоровна","Матрёна Фёдоровна","F",["~1824",""],"D07","жена Ивана Ивановича (~1815)","cano60")
spouse("SP06","Королёва","Прасковья","Фёдоровна","Прасковья Фёдоровна Королёва","F",["1883","1969"],"D10","жена Василия Ивановича; брак 30.06.1908","cano570")
spouse("SP07","Абрамова","Евдокия","","Евдокия Абрамова","F",["24.01.1911","25.01.1989"],"D11","жена Григория 1912","gedcom")
spouse("SP08","Ковригина","Александра","","Александра Ковригина","F",["11.01.1931","07.02.2010"],"D12","жена Василия 1930; с. Б. Болдино","gedcom")
spouse("SP09","Сальникова","Ольга","","Ольга Сальникова","F",["24.09.1956",""],"D13","жена Григория 1954 (развод); г. Остров Псковской обл.","gedcom")
spouse("SP10","","Людмила","Эдуардовна","Людмила Эдуардовна","F",["",""],"D13","вторая жена Григория 1954","gedcom")
spouse("SP11","Ермолин","Дмитрий","","Дмитрий Ермолин","M",["19.12.1956",""],"S12","муж Елены 1959","gedcom")
spouse("SP12","","Нина","","Нина","F",["",""],"S10","жена Николая 1936","gedcom")
spouse("SP13","","Анна","Филипповна","Анна Филипповна","F",["",""],"S02","жена Кондратия Андреевича","vgd140")

# ===== Семьи супругов =====
def fam(id,surname,given,patronymic,full,dates,child_of,note,src):
    add({"id":id,"surname":surname,"given_name":given,"patronymic":patronymic,"full_name":full,"sex":"M",
    "birth":{"date":dates[0],"place":""},"death":{"date":dates[1] if len(dates)>1 else "","place":"","cause":""},
    "status":"CONFIRMED","category":"spouse_family","generation":0,"relation_to_direct_line":"родственник по браку",
    "social_estate":"","occupation":"","religion":"","notes":note,
    "relationships":{"father":None,"mother":None,"spouses":[],"children":child_of},
    "sources":[SRC[src]],"events":[]})

fam("F01","Ковригин","Андрей","","Андрей Ковригин",["1895","19.04.1960"],["SP08"],"отец Александры Ковригиной","gedcom")
fam("F02","Ковригин","Иван","","Иван Ковригин",["1852","1937"],["F01"],"дед Александры Ковригиной","gedcom")
fam("F03","Ковригин","Максим","","Максим Ковригин",["",""],["F02"],"прадед Александры Ковригиной","gedcom")
fam("F04","Дворникова","Евдокия","","Евдокия Дворникова",["14.03.1896","07.10.1978"],["SP08"],"мать Александры Ковригиной","gedcom")
fam("F05","Дворников","Николай","","Николай Дворников",["",""],["F04"],"отец Евдокии Дворниковой","gedcom")
fam("F06","Королёв","Фёдор","","Фёдор Королёв",["",""],["SP06"],"отец Прасковьи Королёвой","gedcom")
fam("F07","Абрамов","Никита","","Никита Абрамов",["",""],["SP07"],"отец Евдокии Абрамовой","gedcom")
fam("F08","Абрамов","Ермолай","","Ермолай Иванович Абрамов",["",""],["F07"],"дед Евдокии Абрамовой","gedcom")
fam("F09","","Анна","","Анна",["","1948"],["SP07"],"мать Евдокии Абрамовой","gedcom")
fam("F10","","Фёдор","","Фёдор",["",""],["F09"],"отец Анны (матери Евдокии)","gedcom")

# ===== Поруновы =====
add({"id":"P01","surname":"Порунов","given_name":"Николай","patronymic":"Александрович","full_name":"Николай Александрович Порунов","sex":"M",
"birth":{"date":"~1930-е","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"CONFIRMED","category":"porunov","generation":10,"relation_to_direct_line":"двоюродный брат Василия Григорьевича Сустатова (1930) и Николая Григорьевича (1936)",
"social_estate":"","occupation":"","religion":"","notes":"мемуары Н.Г. Сустатова: «я и мой двоюродный брат Порунов Николай Александрович пасли в ночном колхозных лошадей»",
"relationships":{"father":"P02","mother":None,"spouses":[],"children":[]},
"sources":[SRC["sarpust3"]],"events":[]})

add({"id":"P02","surname":"Порунов","given_name":"Александр","patronymic":"Павлович","full_name":"Александр Павлович Порунов","sex":"M",
"birth":{"date":"1912","place":"с. Кошелиха"},"death":{"date":"29.12.1942","place":"Сталинградская обл., Котельниковский р-н, х. Цыган-Нацмен","cause":"погиб (ВОВ)"},
"status":"PROBABLE","category":"porunov","generation":9,"relation_to_direct_line":"вероятный отец Николая Александровича (по отчеству)",
"social_estate":"","occupation":"ефрейтор ЮФ 17 отд. Гв. бат. минеров","religion":"","notes":"погиб в ВОВ",
"relationships":{"father":"P03","mother":None,"spouses":[],"children":["P01"]},
"sources":[SRC["vgd20"]],"events":[{"type":"death","date":"29.12.1942","note":"погиб"}]})

add({"id":"P03","surname":"Порунов","given_name":"Павел","patronymic":"Егорович","full_name":"Павел Егорович Порунов","sex":"M",
"birth":{"date":"~1885–1890","place":"с. Кошелиха"},"death":{"date":"","place":"","cause":""},
"status":"PROBABLE","category":"porunov","generation":8,"relation_to_direct_line":"вероятный дед Николая Александровича",
"social_estate":"","occupation":"плотник","religion":"","notes":"плотник Кошелихинского лесозавода № 27 (1919); брак с Клейменовой Анной Васильевной",
"relationships":{"father":None,"mother":None,"spouses":[],"children":["P02","P04"]},
"sources":[SRC["vgd270"],SRC["vgd160"]],"events":[]})

add({"id":"P04","surname":"Порунов","given_name":"Иван","patronymic":"Павлович","full_name":"Иван Павлович Порунов","sex":"M",
"birth":{"date":"1922","place":"с. Кошелиха"},"death":{"date":"14.05.1942","place":"Тульская обл., Белевский р-н","cause":"погиб (ВОВ)"},
"status":"CONFIRMED","category":"porunov","generation":9,"relation_to_direct_line":"вероятный дядя Николая Александровича",
"social_estate":"","occupation":"красноармеец 201 танк. бр.","religion":"","notes":"погиб в ВОВ",
"relationships":{"father":"P03","mother":None,"spouses":[],"children":[]},
"sources":[SRC["vgd20"]],"events":[]})

# ===== Неизвестный Иван (отец Никиты) =====
add({"id":"D02","surname":"","given_name":"Иван","patronymic":"","full_name":"Иван (?)","sex":"M",
"birth":{"date":"~кон. XVII в.","place":"дворцовая деревня Сыресева"},"death":{"date":"","place":"","cause":""},
"status":"HYPOTHESIS","category":"direct","generation":0,"relation_to_direct_line":"отец Никиты Ивановича (не идентифицирован)",
"social_estate":"","occupation":"","religion":"","notes":"отец Никиты Иванова; в источниках не найден; возможно записан под эрзянским именем до крещения",
"relationships":{"father":None,"mother":None,"spouses":[],"children":["D03"]},
"sources":[],"events":[]})

# ===== Запись =====
for pid, d in P.items():
    fp = os.path.join(OUT, pid + ".json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

# index
idx = {pid: {"full_name": d["full_name"], "category": d["category"], "status": d["status"], "birth": d["birth"]["date"], "death": d["death"]["date"]} for pid, d in sorted(P.items())}
with open("/home/igor/cursorwork/sustatov/opencode/index.json", "w", encoding="utf-8") as f:
    json.dump(idx, f, ensure_ascii=False, indent=2)

print("Всего персон:", len(P))
