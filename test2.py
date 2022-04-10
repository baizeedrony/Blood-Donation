from flask import blueprints,render_template



cur=connection.cursor()
cur.execute('select *from tab')
while True:
    row=cur.fetchone()
    if not row:
        break
        end