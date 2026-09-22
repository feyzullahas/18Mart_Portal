file_path = 'c:/Users/feyzu/Desktop/Projeler/18Mart_Portal/api/app/database.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('        print("[OK] Database tablolari basariyla olusturuldu")', '    print("[OK] Database tablolari basariyla olusturuldu")')
content = content.replace('        except Exception as e:', 'except Exception as e:')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
