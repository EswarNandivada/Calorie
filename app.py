from flask import flash,Flask,render_template,redirect,url_for,jsonify,request,session
from flask_mysqldb import MySQL
from datetime import datetime,timedelta
from datetime import date
from flask_session import Session
app=Flask(__name__)
app.secret_key='A@Bullela@_3'
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']='Eswar@2001'
app.config['MYSQL_DB']='callorie'
app.config["SESSION_TYPE"]="filesystem"
mysql=MySQL(app)
Session(app)
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/homepage/<id1>',methods=['GET','POST'])
def homepage(id1):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select target from users where id=%s',[id1])
        target=cursor.fetchone()[0]
        cursor.execute('select consumed from users where id=%s',[id1])
        consumed=cursor.fetchone()[0]
        cursor.execute('select workouttarget from users where id=%s',[id1])
        worktarget=cursor.fetchone()[0]
        cursor.execute('select workoutconsumed from users where id=%s',[id1])
        workconsumed=cursor.fetchone()[0]
        current_date=date.today()
        current_date=f"{current_date.year}-{current_date.month}-{current_date.day}"
        today_date=datetime.strptime(current_date,'%Y-%m-%d')
        date_today=datetime.strftime(today_date,'%Y-%m-%d')
        seven_back=date.today()-timedelta(days=7)
        seven_days_back=datetime.strftime(seven_back,'%Y-%m-%d')
        cursor.execute('select item,category,sum(quantity),sum(carbohydrates),sum(fats),sum(protein),sum(fiber),sum(callories) from callorie_track where id=%s and date=%s group by item order by category asc',[id1,date_today])
        day_report=cursor.fetchall()
        cursor.execute('select item,category,sum(quantity),sum(carbohydrates),sum(fats),sum(protein),sum(fiber),sum(callories) from callorie_track where id=%s and date>=%s group by item order by category asc',[id1,seven_days_back])
        sevendays_report=cursor.fetchall()
        cursor.execute('select workout,sum(time),sum(callories) from workout_track where id=%s and date=%s group by workout',[session.get('user'),date_today])
        day_report_w=cursor.fetchall()
        cursor.execute('select workout,sum(time),sum(callories) from workout_track where id=%s and date>=%s group by workout',[session.get('user'),seven_days_back])
        sevendays_report_w=cursor.fetchall()
        cursor.close()
        if request.method=='POST':
            if 'target' in [i for i in request.form]:
                target=request.form['target']
                cursor=mysql.connection.cursor()
                cursor.execute('update users set target=%s where id=%s',[target,id1])
                mysql.connection.commit()
                cursor.close()
            if 'worktarget' in [i for i in request.form]:
                worktarget=request.form['worktarget']
                cursor=mysql.connection.cursor()
                cursor.execute('update users set workouttarget=%s where id=%s',[worktarget,id1])
                mysql.connection.commit()
                cursor.close()
            return render_template('profile.html',target=target,id1=id1,consumed=consumed,worktarget=worktarget,workconsumed=workconsumed,day_report=day_report,sevendays_report=sevendays_report,day_report_w=day_report_w,sevendays_report_w=sevendays_report_w)
        return render_template('profile.html',target=target,id1=id1,consumed=consumed,worktarget=worktarget,workconsumed=workconsumed,day_report=day_report,sevendays_report=sevendays_report,day_report_w=day_report_w,sevendays_report_w=sevendays_report_w)
    return redirect(url_for('login'))
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        id1=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT ID from users')
        users=cursor.fetchall()
        cursor.close()
        if (id1,) in users:
            flash('User Id already Exists')
            return render_template('registration.html')
        name=request.form['name']
        email=request.form['email']
        number=request.form['number']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO users (id,name,email,mobile_no,password) values(%s,%s,%s,%s,%s)',[id1,name,email,number,password])
        mysql.connection.commit()
        cursor.close()
        flash('Details registered successfully')
        return render_template('registration.html')
    return render_template('registration.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('homepage',id1=session['user']))
    if request.method=="POST":
        user=request.form['user']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT id from users')
        users=cursor.fetchall()            
        password=request.form['password']
        cursor.execute('select password from users where id=%s',[user])
        data=cursor.fetchone()
        cursor.close() 
        if (user,) in users:
            if password==data[0]:
                session['user']=user
                return redirect(url_for('homepage',id1=user))
            else:
                flash('Invalid Password')
                return render_template('login.html')
        else:
            flash('Invalid user id')
            return render_template('login.html')      
    return render_template('login.html')
@app.route('/addfood',methods=['GET','POST'])
def addfood():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        today=date.today()
        current_date=datetime.strptime(f'{str(today.year)}-{str(today.month)}-{str(today.day)}','%Y-%m-%d')
        cursor.execute('SELECT item from items order by category asc')
        items=cursor.fetchall()
        cursor.execute('SELECT target from users where id=%s',[session.get('user')])
        target=int(cursor.fetchone()[0])
        current_date=date.today()
        current_date=f"{current_date.year}-{current_date.month}-{current_date.day}"
        today_date=datetime.strptime(current_date,'%Y-%m-%d')
        date_today=datetime.strftime(today_date,'%Y-%m-%d')
        cursor.execute('select item,category,sum(quantity),sum(carbohydrates),sum(fats),sum(protein),sum(fiber),sum(callories) from callorie_track where id=%s and date=%s group by item',[session.get('user'),date_today])
        day_report=cursor.fetchall()
        cursor.close()
        if target==0:
            flash('Set the target first!')
            return render_template('addfood.html',id1=session['user'],items=items)
        if request.method=="POST":
            cursor=mysql.connection.cursor()
            item=request.form['item']
            category=request.form['category']
            quantity=int(request.form['quantity'])
            cursor.execute('SELECT carbohydrates,fats,protein,fiber,calorie from items where item=%s',[item])
            cal_data=cursor.fetchone()
            carbohydrates=round(quantity*(cal_data[0]/100),2)
            fats=round(quantity*(cal_data[1]/100),2)
            protein=round(quantity*(cal_data[2]/100),2)
            fiber=round(quantity*(cal_data[3]/100),2)
            calories=round(quantity*(cal_data[4]/100),2)
            cursor.execute('SELECT consumed from users where id=%s',[session.get('user')])
            consumed=round(float(cursor.fetchone()[0]),2)+calories
            cursor.execute('update users set consumed=%s where id=%s',[consumed,session.get('user')])
            cursor.execute('insert into callorie_track (id,item,category,quantity,carbohydrates,fats,protein,fiber,callories,date) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[session.get('user'),item,category,quantity,carbohydrates,fats,protein,fiber,calories,current_date])
            mysql.connection.commit()
            cursor.execute('select item,category,sum(quantity),sum(carbohydrates),sum(fats),sum(protein),sum(fiber),sum(callories) from callorie_track where id=%s and date=%s group by item',[session.get('user'),date_today])
            day_report=cursor.fetchall()
            cursor.close()
            return render_template('addfood.html',id1=session['user'],items=items,day_report=day_report)
        return render_template('addfood.html',id1=session['user'],items=items,day_report=day_report)
    return redirect(url_for('login'))
@app.route('/addworkout',methods=['GET','POST'])
def addwork():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        today=date.today()
        current_date=datetime.strptime(f'{str(today.year)}-{str(today.month)}-{str(today.day)}','%Y-%m-%d')
        cursor.execute('SELECT workout from workout')
        workouts=cursor.fetchall()
        cursor.execute('SELECT workouttarget from users where id=%s',[session.get('user')])
        workouttarget=int(cursor.fetchone()[0])
        current_date=date.today()
        current_date=f"{current_date.year}-{current_date.month}-{current_date.day}"
        today_date=datetime.strptime(current_date,'%Y-%m-%d')
        date_today=datetime.strftime(today_date,'%Y-%m-%d')
        cursor.execute('select workout,sum(time),sum(callories) from workout_track where id=%s and date=%s group by workout',[session.get('user'),date_today])
        day_report=cursor.fetchall()
        cursor.close()
        if workouttarget==0:
            flash('Set the target first!')
            return render_template('addworkout.html',id1=session['user'],workouts=workouts)
        if request.method=="POST":
            cursor=mysql.connection.cursor()
            time=float(request.form['time'])
            category=request.form['category']
            cursor.execute('SELECT time,callories from workout where workout=%s',[category])
            cal_data=cursor.fetchone()
            calories=round(time*(cal_data[1]/cal_data[0]),2)
            cursor.execute('SELECT workoutconsumed from users where id=%s',[session.get('user')])
            consumed=round(float(cursor.fetchone()[0]),2)+calories
            cursor.execute('update users set workoutconsumed=%s where id=%s',[consumed,session.get('user')])
            cursor.execute('insert into workout_track (workout,time,id,callories,date) values(%s,%s,%s,%s,%s)',[category,time,session.get('user'),calories,current_date])
            mysql.connection.commit()
            cursor.execute('select workout,sum(time),sum(callories) from workout_track where id=%s and date=%s group by workout',[session.get('user'),date_today])
            day_report=cursor.fetchall()
            cursor.close()
            return render_template('addworkout.html',id1=session['user'],workouts=workouts,day_report=day_report)
        return render_template('addworkout.html',id1=session['user'],workouts=workouts,day_report=day_report)
    return redirect(url_for('login'))
@app.route('/logout')
def logout():
    session['user']=None
    return redirect(url_for('home'))
@app.route('/view')
def view():
    return render_template('details.html')
app.run(debug=True,use_reloader=True)
