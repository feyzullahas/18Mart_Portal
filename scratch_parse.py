import re

raw_kyk = """
1 Ekim Perşembe (880 kcal): Haşlanmış Yumurta (1 adet L boy), Patates Kavurması 150 g, Karışık Pizza 150 g, Krem Peynir 20 g
2 Ekim Cuma (900 kcal): Menemen 150 g (1 adet L boy yumurta), Patates Kızartması 150 g, Çikolatalı Milföy Börek 60 g, Beyaz Peynir 40 g
3 Ekim Cumartesi (920 kcal): Haşlanmış Yumurta, Karışık Kızartma 150 g, Simit 1 adet, Kaşar Peyniri 40 g
4 Ekim Pazar (880 kcal): Sade Omlet (1 adet L boy yumurta, 70 g), Salçalı Sosis 100 g, Peynirli/Ispanaklı Börek 120 g, Beyaz Peynir 40 g
5 Ekim Pazartesi (900 kcal): Haşlanmış Yumurta, Patates Kızartması 150 g, Zeytinli/Peynirli Açma 1 adet, Kaşar Peyniri 40 g
6 Ekim Salı (890 kcal): Kaşarlı Omlet (25 g kaşar + 1 adet L boy yumurta, 100 g), Patates Salatası 150 g, Dere Otlu Poğaça 1 adet, Labne Peynir 20 g
7 Ekim Çarşamba (880 kcal): Haşlanmış Yumurta, Sosis Kızartma 100 g, Peynirli/Ispanaklı Börek 120 g, Beyaz Peynir 40 g
8 Ekim Perşembe (870 kcal): Sucuklu Omlet (1 adet L boy yumurta + 25 g beyaz etli sucuk, 100 g), Kekikli Domates Biber Kızartma 100 g, Kakaolu Kek 50 g, Ezine Peyniri 40 g
9 Ekim Cuma (910 kcal): Haşlanmış Yumurta, Patates Kızartması 150 g, Simit 1 adet, Beyaz Peynir 40 g
10 Ekim Cumartesi (880 kcal): Peynirli Omlet (30 g beyaz peynir + 1 adet L boy yumurta, 100 g), Patates Kavurması 150 g, Sosisli Milföy Börek 60 g, Kaşar Peyniri 40 g
11 Ekim Pazar (870 kcal): Haşlanmış Yumurta, Patates Kroket 60 g, Karışık Pizza 150 g, Beyaz Peynir 40 g
12 Ekim Pazartesi (900 kcal): Sade Omlet (70 g), Patates Kızartması 150 g, Çikolatalı Milföy Börek 60 g, Kaşar Peyniri 40 g
13 Ekim Salı (850 kcal): Haşlanmış Yumurta, Salçalı Sosis 100 g, Sade Poğaça 1 adet, Çeçil Peyniri 40 g
14 Ekim Çarşamba (910 kcal): Kaşarlı Omlet (25 g kaşar + 1 yumurta, 100 g), Karışık Kızartma 150 g, Zeytinli/Peynirli Açma 1 adet, Beyaz Peynir 40 g
15 Ekim Perşembe (880 kcal): Haşlanmış Yumurta, Patates Salatası 150 g, Pankek + Sürülebilir Çikolata (2 adet + 20 g), Kaşar Peyniri 40 g
16 Ekim Cuma (900 kcal): Menemen 150 g (1 adet L boy yumurta), Patates Kızartması 150 g, Simit 1 adet, Krem Peynir 20 g
17 Ekim Cumartesi (890 kcal): Haşlanmış Yumurta, Salçalı Sosis 100 g, Peynirli/Ispanaklı Börek 120 g, Tulum Peyniri 40 g
18 Ekim Pazar (920 kcal): Sucuklu Omlet (1 yumurta + 25 g beyaz etli sucuk, 100 g), Patates Kavurması 150 g, Pişi + Reçel (120 g + 20 g), Beyaz Peynir 40 g
19 Ekim Pazartesi (890 kcal): Haşlanmış Yumurta, Sosis Kızartma 100 g, Dereotlu Poğaça 1 adet, Kaşar Peyniri 40 g
20 Ekim Salı (880 kcal): Peynirli Omlet (30 g beyaz peynir + 1 yumurta, 100 g), Patates Kroket 60 g, Karışık Pizza 150 g, Beyaz Peynir 40 g
21 Ekim Çarşamba (880 kcal): Haşlanmış Yumurta, Patates Kızartması 150 g, Sade Poğaça 1 adet, Labne Peynir 20 g
22 Ekim Perşembe (900 kcal): Sade Omlet (70 g), Patates Salatası 150 g, Çikolatalı Milföy Börek 60 g, Kaşar Peyniri 40 g
23 Ekim Cuma (850 kcal): Haşlanmış Yumurta, Patates Kızartması 150 g, Peynirli/Ispanaklı Börek 120 g, Beyaz Peynir 40 g
24 Ekim Cumartesi (900 kcal): Kaşarlı Omlet (25 g kaşar + 1 yumurta, 100 g), Karışık Kızartma 150 g, Simit 1 adet, Ezine Peyniri 40 g
25 Ekim Pazar (920 kcal): Haşlanmış Yumurta, Patates Kroket 60 g, Yumurtalı Ekmek (2 dilim tost ekmeği), Beyaz Peynir 40 g
26 Ekim Pazartesi (890 kcal): Mantarlı Omlet (30 g pişmiş mantar + 1 yumurta, 100 g), Patates Salatası 150 g, Dere Otlu Poğaça 1 adet, Krem Peynir 20 g
27 Ekim Salı (880 kcal): Haşlanmış Yumurta, Patates Kızartması 150 g, Peynirli/Ispanaklı Börek 120 g, Beyaz Peynir 40 g
28 Ekim Çarşamba (900 kcal): Sucuklu Omlet (1 yumurta + 25 g beyaz etli sucuk, 100 g), Patates Kavurması 150 g, Zeytinli/Peynirli Açma 1 adet, Kaşar Peyniri 40 g
29 Ekim Perşembe (890 kcal): Menemen 150 g (1 adet L boy yumurta), Sosis Kızartma 100 g, Basma Pide 120 g, Beyaz Peynir 40 g
30 Ekim Cuma (880 kcal): Sade Omlet (70 g), Patates Kroket 60 g, Simit 1 adet, Çeçil Peyniri 40 g
31 Ekim Cumartesi (860 kcal): Haşlanmış Yumurta, Salçalı Sosis 100 g, Peynirli/Ispanaklı Börek 120 g, Kaşar Peyniri 40 g

1 Ekim Perşembe (950 kcal): Ezogelin Çorba - Salçalı Şehriye Çorba / Tavuk Şiş+Garnitür - Mücver+Yoğurt (200 g (100 g et) / 200 g) / Makarna (Sos Çeşitleri ile) 200 g / Çoban Salata 150 g
2 Ekim Cuma (850 kcal): Düğün Çorba - Şafak Çorba / Kuru Fasulye - Sebze Graten (200 g / 200 g) / Pirinç Pilavı 150 g / Cacık 150 g / Supangle 150 g
3 Ekim Cumartesi (900 kcal): Mercimek Çorba - Sebze Çorba / Çoban Kavurma - Köri Soslu Tavuk - Bezelye Yemeği (%40-%40-%20) / Bulgur Pilavı 200 g / Ayran 170-200 ml
4 Ekim Pazar (890 kcal): Domates Çorba - Terbiyeli Şehriye Çorba / Tavuk Külbastı+Garnitür - Biber Dolma+Yoğurt (%70-%30) / Spagetti Napoliten 200 g / Karışık Salata 100 g
5 Ekim Pazartesi (880 kcal): Ezogelin Çorba - Kremalı Mantar Çorba / Karnıyarık - Taze Fasulye (200 g (60 g et) / 200 g) / Şehriyeli Pirinç Pilavı 150 g / Cacık 150 g
6 Ekim Salı (910 kcal): Tarhana Çorba - Havuç Çorba / Galeta Unlu Tavuk+Garnitür - Yeşil Mercimek Yemeği (%90-%10) / Sebzeli Bulgur Pilavı 200 g / Kremşantili Haşhaşlı Revani 100 g
7 Ekim Çarşamba (930 kcal): Yayla Çorba - Mercimek Çorba / Izgara Köfte+Garnitür - Izgara Tavuk+Garnitür - Mücver+Yoğurt (%40-%40-%20) / Salçalı Makarna 200 g / Trileçe 150 g
8 Ekim Perşembe (910 kcal): Salçalı Şehriye Çorba - Toyga Çorba / Tavuk Fajita - Patates Oturtma - Sebze Graten (%40-%40-%20) / Pirinç Pilavı 150 g / Kaşık Salata 150 g
9 Ekim Cuma (900 kcal): Mahluta Çorba - Köz Biber Çorba / Hünkâr Beğendi (kuşbaşı etli) - Tavuk Pirzola+Garnitür - Bezelye Yemeği (%40-%40-%20) / Bulgur Pilavı 200 g / Haydari 100 g
10 Ekim Cumartesi (890 kcal): Ezogelin Çorba - Sebze Çorba / Tavuk Külbastı+Garnitür - Biber Dolma+Yoğurt (%70-%30) / Cevizli Erişte 200 g / Ege Salata 150 g
11 Ekim Pazar (850 kcal): Tarhana Çorba - Düğün Çorba / Nohut Yemeği - İmam Bayıldı (200 g / 200 g) / Şehriyeli Pirinç Pilavı 150 g / Cevizli Baklava 100 g
12 Ekim Pazartesi (910 kcal): Mercimek Çorba - Kremalı Mantar Çorba / Tas Kebabı - Beşamel Soslu Tavuk - Karnabahar Kızartma+Yoğurt (%40-%40-%20) / Salçalı Bulgur Pilavı 200 g / Havuç Aysberg Salata 100 g
13 Ekim Salı (930 kcal): Çeşmi Nigar Çorba - Salçalı Şehriye Çorba / Izgara Tavuk+Garnitür - Patlıcan Musakka - Barbunya Yemeği (%50-%30-%20) / Pirinç Pilavı 150 g / Çikolatalı Kremalı Pasta 120 g
14 Ekim Çarşamba (950 kcal): Tarhana Çorba - Havuç Çorba / Hamburger - Taze Fasulye (%90-%10) / Patates Kızartması+Ketçap+Mayonez 150 g / Ayran veya Meyve Suyu 170-200 ml
15 Ekim Perşembe (930 kcal): Yayla Çorba - Ezogelin Çorba / Galeta Unlu Tavuk+Garnitür - Türlü Yemeği (%90-%10) / Sebzeli Bulgur Pilavı 200 g / Çoban Salata 150 g
16 Ekim Cuma (900 kcal): Düğün Çorba - Domates Çorba / Kuru Fasulye - Sebze Graten / Şehriyeli Pirinç Pilavı 150 g / Cacık 150 g / Fındıklı Şekerpare 100 g
17 Ekim Cumartesi (910 kcal): Terbiyeli Şehriye Çorba - Mahluta Çorba / Lavaşta Tavuk Tantuni - Bezelye Yemeği (%90-%10) / Spagetti Napoliten 200 g / Ayran 170-200 ml
18 Ekim Pazar (920 kcal): Mercimek Çorba - Köz Biber Çorba / Orman Kebabı - Tavuk Şiş+Garnitür - Kabak Sandal (%40-%40-%20) / Bulgur Pilavı 200 g / Havuç Tarator 100 g
19 Ekim Pazartesi (930 kcal): Tarhana Çorba - Yayla Çorba / Tavuk Fajita - Karnabahar Kızartma+Yoğurt / Makarna (Sos Çeşitleri ile) 200 g / Cevizli Baklava 100 g
20 Ekim Salı (910 kcal): Çeşmi Nigar Çorba - Salçalı Şehriye Çorba / Biga Köfte+Garnitür - Tavuk Külbastı+Garnitür - Mantar Sote (%40-%40-%20) / Pirinç Pilavı 150 g / Cacık 150 g
21 Ekim Çarşamba (900 kcal): Sebze Çorba - Ezogelin Çorba / Köri Soslu Tavuk - Mücver+Yoğurt / Spagetti Napoliten 200 g / Karışık Salata 100 g
22 Ekim Perşembe (890 kcal): Domates Çorba - Düğün Çorba / Nohut Yemeği - Taze Fasulye (200 g / 200 g) / Domatesli Bulgur Pilavı 200 g / Ezme 100 g / Sütlaç 150 g
23 Ekim Cuma (910 kcal): Mercimek Çorba - Havuç Çorba / Misket Köfte - Tavuk Sote - Türlü (%40-%40-%20) / Cevizli Erişte 200 g / Kaşık Salata 150 g
24 Ekim Cumartesi (940 kcal): Tarhana Çorba - Kremalı Mantar Çorba / Galeta Unlu Tavuk+Garnitür - Bezelye Yemeği (%90-%10) / Şehriyeli Pirinç Pilavı 150 g / Çiğköfte 100 g
25 Ekim Pazar (920 kcal): Çeşmi Nigar Çorba - Köz Biber Çorba / Çökertme Kebabı - Tavuk Pirzola+Garnitür - Falafel+Yoğurt (%40-%40-%20) / Bulgur Pilavı 200 g / Kalburabastı 100 g
26 Ekim Pazartesi (930 kcal): Ezogelin Çorba - Sebze Çorba / Izgara Tavuk+Garnitür - Püreli Et Sote - Biber Dolma+Yoğurt (%40-%30-%30) / Salçalı Makarna 200 g / Havuç Aysberg Salata 100 g
27 Ekim Salı (900 kcal): Düğün Çorba - Tarhana Çorba / Kuru Fasulye - Sebze Graten (200 g / 200 g) / Pirinç Pilavı 150 g / Yoğurt 120 g / Tiramisu 120 g
28 Ekim Çarşamba (920 kcal): Mercimek Çorba - Anadolu Çorba / Et Fajita+Lavaş - Tavuk Fajita+Lavaş - Karnabahar Kızartma+Yoğurt (%40-%30-%30) / Sebzeli Bulgur Pilavı 200 g / Çoban Salata 150 g
29 Ekim Perşembe (910 kcal): Domates Çorba - Yayla Çorba / Tavuk Sarma - Taze Fasulye / Makarna (Sos Çeşitleri ile) 200 g / Haydari 100 g
30 Ekim Cuma (950 kcal): Tavuk Çorba - Çeşmi Nigar Çorba / Hamburger - İmam Bayıldı (%90-%10) / Patates Kızartması+Ketçap+Mayonez 150 g / Ayran veya Meyve Suyu 170-200 ml
31 Ekim Cumartesi (930 kcal): Salçalı Şehriye Çorba - Yüksük Çorba / Püreli Et Sote - Püreli Tavuk Sote - Barbunya Yemeği (%40-%40-%20) / Şehriyeli Pirinç Pilavı 150 g / Supangle 150 g
"""

days_b = {}
days_d = {}
cals_b = {}
cals_d = {}

for line in raw_kyk.strip().split('\n'):
    if not line.strip(): continue
    match = re.match(r'^(\d+)\s+Ekim\s+(\w+)\s+\((\d+)\s+kcal\):\s+(.*)', line)
    if match:
        day = int(match.group(1))
        day_name = match.group(2)
        cals = int(match.group(3))
        items_str = match.group(4)
        if day in days_b and day in days_d: continue # avoid re-adding
        
        # Determine if breakfast or dinner based on whether day is already in days_b
        if day not in days_b:
            # breakfast
            items = [x.strip() for x in items_str.split(',')]
            days_b[day] = items
            cals_b[day] = cals
        else:
            # dinner
            items = [x.strip() for x in items_str.split('/')]
            days_d[day] = items
            cals_d[day] = cals

with open('scratch_out.py', 'w', encoding='utf-8') as f:
    f.write('_OCTOBER_2026 = [\n')
    for d in range(1, 32):
        if d in days_b and d in days_d:
            b_list = repr(days_b[d])
            d_list = repr(days_d[d])
            date_tr = f'"{d} Ekim 2026 {list(["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"])[(d+2)%7]}"'
            f.write(f'    _day("2026-10-{d:02d}", {date_tr}, {b_list}, {d_list}, total_calories_breakfast={cals_b[d]}, total_calories_dinner={cals_d[d]}),\n')
    f.write(']\n')

raw_osem = """
* **1 Ekim 2026, Perşembe:** Tarhana Çorba (194), Hünkarbeğendi (446), Tel Şeh.Pirinç Pilavı (345), Ballı Balım (380)[cite: 3]
* **2 Ekim 2026, Cuma:** Mercimek Çorba (233), Köri Soslu Tavuk (389), Sebzeli Bulgur Pilavı (288), Cacık (118)[cite: 3]
* **5 Ekim 2026, Pazartesi:** Ezogelin Çorba (230), Et Döner (318), Köz Domates Biber (18), Arpa Şehriye Pilavı (360), Ayran (74)[cite: 3]
* **6 Ekim 2026, Salı:** Buğday Çorba (164), Izgara Tavuk Kanat (386), Patates Püresi (137), Garn. Pirinç Pilavı (359), Cevizli Baklava (482)[cite: 3]
* **7 Ekim 2026, Çarşamba:** Mercimek Çorba (233), Tas Kebabı (374), Su Böreği (430), Karışık Salata (70)[cite: 3]
* **8 Ekim 2026, Perşembe:** Düğün Çorba (174), Sebzeli Tavuk Kebabı (301), Salçalı Makarna (321), Fıstıklı İrmik Helvası (480)[cite: 3]
* **9 Ekim 2026, Cuma:** Domates Çorba (153), Ekşili Köfte (467), Şehriyeli Kuskus (353), Yoğurt (124)[cite: 3]
* **12 Ekim 2026, Pazartesi:** Tel Şehriye Çorba (124), Etli Kuru Fasulye (382), Bahar Pilavı (259), Biber Borani (117)[cite: 3]
* **13 Ekim 2026, Salı:** Ezogelin Çorba (230), Tavuk Kavurma (317), Yoğurtlu Mantı (381), Muz (128)[cite: 3]
* **14 Ekim 2026, Çarşamba:** Tavuksuyu Çorba (198), İzmir Köfte (442), Erişte Kavurma (235), Peynir Tatlısı (261)[cite: 3]
* **15 Ekim 2026, Perşembe:** Kre. Mantar Çorba (151), Tavuk But (395), Marul Salatası (61), Arpa Şehriye Pilavı (360), Ayran (74)[cite: 3]
* **16 Ekim 2026, Cuma:** Mercimek Çorba (233), Et Sote (370), Patates Püresi (137), Makarna Kavurma (310), Islak Kek (301)[cite: 3]
* **19 Ekim 2026, Pazartesi:** Ezogelin Çorba (230), Tavuk Şinitzel (414), Haydari (18), Mısırlı Kuskus (323), Ayran (74)[cite: 3]
* **20 Ekim 2026, Salı:** Yayla Çorba (239), Patlıcan Musakka (439), Zerd. Bulgur Pilavı (270), Yoğ. Közl. Kapya Biber (126)[cite: 3]
* **21 Ekim 2026, Çarşamba:** Lebeniye Çorba (151), Ali Nazik (359), Tel Şeh.Pirinç Pilavı (345), Tulumba Tatlısı (495)[cite: 3]
* **22 Ekim 2026, Perşembe:** Düğün Çorba (174), Tavuk Sote (328), Sosyete Mantısı (357), Çoban Salata (75)[cite: 3]
* **23 Ekim 2026, Cuma:** Arpa Şehriye Çorba (167), İslim Köfte (418), Peynirli Erişte (264), Sakızlı Muhallebi (177)[cite: 3]
* **26 Ekim 2026, Pazartesi:** Kre. Brokoli Çorba (151), Kadınbudu Köfte (477), Haydari (55), Dom. Sos. Makarna (317), Meyve Suyu (100)[cite: 3]
* **27 Ekim 2026, Salı:** Tavuksuyu Çorba (198), Ankara Tava (511), Karışık Kızartma (335), Yoğurt (124)[cite: 3]
* **28 Ekim 2026, Çarşamba:** Domates Çorba (153), Çıtır Tavuk (314), Küp Patates (151), Peynirli Börek (430), Kakaolu Puding (219)[cite: 3]
* **29 Ekim 2026, Perşembe:** Ezogelin Çorba (230), Buğu Kebabı (453), Arpa Şehriye Pilavı (360), Revani (424)[cite: 3]
"""

with open('scratch_osem_out.py', 'w', encoding='utf-8') as f:
    f.write('    def _osem_menus_october_2026(self) -> Dict[str, List[tuple]]:\n')
    f.write('        return {\n')
    for line in raw_osem.strip().split('\n'):
        match = re.match(r'\*\s+\*\*(\d+)\s+Ekim\s+2026,\s+\w+:\*\*\s+(.*)\[cite', line)
        if match:
            day = int(match.group(1))
            items_str = match.group(2)
            items = [x.strip() for x in items_str.split(',')]
            out_items = []
            for item in items:
                m2 = re.match(r'(.*)\((\d+)\)', item)
                if m2:
                    out_items.append(f'("{m2.group(1).strip()}", {m2.group(2)})')
                else:
                    out_items.append(f'("{item.strip()}", None)')
            f.write(f'            "2026-10-{day:02d}": [{", ".join(out_items)}],\n')
    f.write('        }\n')

