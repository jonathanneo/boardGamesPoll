from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PollForm, OptionForm, ResetPasswordRequestForm
from app.forms import EditPollForm, EditOptionForm, DeleteUserForm, MakeUserAdminForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Poll, Option, votes
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from sqlalchemy import func
from flask import request

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PollForm()
    optionForm = OptionForm()
    if form.validate_on_submit(): # if form validation is true 
        poll = Poll(title=form.title.data, body=form.body.data, image_url=form.image_url.data, author=current_user)
        db.session.add(poll)
        db.session.commit()
        flash('Your poll is now live!')
        return redirect(url_for('index')) # return redirect instead of render_template as that will refresh the page and re-submit the form and causes duplicates 
    
    page = request.args.get('page',1,type=int) 
    polls = db.session.query(Poll).filter(Poll.user_id == current_user.id).paginate(
        page, app.config['POLLS_PER_PAGE'], False)
    next_url = url_for('index', page=polls.next_num) if polls.has_next else None 
    prev_url = url_for('index', page=polls.prev_num) if polls.has_prev else None
    
    return render_template("index.html", title='Home Page', form=form, polls=polls.items, next_url=next_url, prev_url=prev_url)

@app.route('/about')
def about():
    return render_template("about.html", title='About Us')

@app.route('/admin')
def admin():
    return render_template("admin.html", title = 'Admin Page')

@app.route('/manage_users')
def manage_users():
    return render_template("manage_users.html", title='Manage Users')

@app.route('/delete_user',methods=['GET', 'POST'])
def delete_user():
    form = DeleteUserForm()
    header_content = 'Delete User'
    if current_user.is_anonymous == True or current_user.is_admin == False:
        flash('You have to be logged in as an admin to access this feature.')
        return redirect(url_for('explore'))
    if form.validate_on_submit():
        username = form.username.data
        user = db.session.query(User).filter(User.username == username).first()
        if user is None:
            flash('Could not find user. Please try again.')
            return redirect(url_for('delete_user')) 
        else: 
            db.session.delete(user)
            db.session.commit()
            flash(user.username + ' has been deleted!')
            return redirect(url_for('delete_user'))
    
    page = request.args.get('page',1,type=int)
    users=db.session.query(User).order_by(User.last_seen.desc()).paginate(
        page, app.config['POLLS_PER_PAGE'], False)
    next_url = url_for('delete_user',page=users.next_num) if users.has_next else None
    prev_url = url_for('delete_user',page=users.prev_num) if users.has_prev else None
    
    return render_template("change_or_delete_user.html", title='Delete Users', users=users.items, 
        form=form,header_content=header_content,next_url=next_url, prev_url=prev_url)

@app.route('/make_user_admin',methods=['GET', 'POST'])
def make_user_admin():
    page = request.args.get('page',1,type=int)
    users=db.session.query(User).order_by(User.last_seen.desc()).paginate(
        page, app.config['POLLS_PER_PAGE'], False)
    next_url = url_for('delete_user',page=users.next_num) if users.has_next else None
    prev_url = url_for('delete_user',page=users.prev_num) if users.has_prev else None
    form = MakeUserAdminForm()
    header_content = 'Make User Admin'
    if current_user.is_anonymous == True or current_user.is_admin == False:
        flash('You have to be logged in as an admin to access this feature.')
        return redirect(url_for('explore'))
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.username == form.username.data).first()
        if user is None:
            flash('Could not find user. Please try again.')
            return redirect(url_for('make_user_admin')) 
        elif user.is_admin:
            flash(user.username + ' is already an admin!')
            redirect(url_for('make_user_admin'))
        elif current_user.is_admin: 
            current_user.make_admin(user)
            db.session.commit()
            flash(user.username + ' is now an admin!')
            return redirect(url_for("make_user_admin"))
    return render_template("change_or_delete_user.html", title='Delete Users', users=users.items, 
        form=form,header_content=header_content,next_url=next_url, prev_url=prev_url)

@app.route('/manage_polls')
def manage_polls():
    page = request.args.get('page',1,type=int)
    polls = Poll.query.order_by(Poll.timestamp.desc()).paginate(
        page, app.config['POLLS_PER_PAGE'], False)
    next_url = url_for('manage_polls', page=polls.next_num) if polls.has_next else None 
    prev_url = url_for('manage_polls', page=polls.prev_num) if polls.has_prev else None
    return render_template('manage_poll.html', title='Manage Polls', polls=polls.items, next_url=next_url, prev_url=prev_url) 

@app.route('/user/<username>/promote')
@login_required
def makeAdmin(username):
    u = User.query.filter_by(username=username).first()
    current_user.make_admin(u)
    db.session.commit()
    flash(username + ' has been promoted as an admin.')
    return user(username)

@app.route('/user/<username>/remove')
@login_required
def removeAdmin(username):
    u = User.query.filter_by(username=username).first()
    current_user.remove_admin(u)
    db.session.commit()
    flash(username + ' has been removed as an admin.')
    return user(username)

@app.route('/addOption/<poll_id>', methods=['GET', 'POST'])
@login_required
def addOption(poll_id):
    form = OptionForm()
    polls = db.session.query(Poll).filter(Poll.id==poll_id).all()[0]
    if form.validate_on_submit():
        option = Option(body=form.body.data, id_poll=poll_id)
        db.session.add(option)
        db.session.commit()
        return redirect(url_for('addOption', poll_id=poll_id))
    
    options = db.session.query(Option).filter(Option.id_poll==poll_id).all()

    return render_template('addOption.html', title='View Poll', form=form, options=options, polls=polls)

@app.route('/vote/<poll_id>/<option_id>')
@login_required
def vote(poll_id, option_id):
    user = current_user
    option = db.session.query(Option).filter(Option.id==option_id).all()[0]
    user.vote(option)
    db.session.commit()
    flash('You have voted for {}'.format(option.body))
    
    return redirect(url_for('viewPoll',poll_id=poll_id))

@app.route('/unvote/<poll_id>/<option_id>')
@login_required
def unvote(poll_id, option_id):
    user = current_user
    option = db.session.query(Option).filter(Option.id==option_id).all()[0]
    user.unvote(option)
    db.session.commit()
    flash('You have unvoted for {}'.format(option.body))
    
    return redirect(url_for('viewPoll', poll_id=poll_id))

@app.route('/deleteOption/<poll_id>/<option_id>')
@login_required
def deleteOption(poll_id, option_id):
    user = current_user
    option = db.session.query(Option).filter(Option.id==option_id).all()[0]
    db.session.delete(option)
    db.session.commit()
    flash('You have deleted option:{}'.format(option.body))
    
    return redirect(url_for('addOption', poll_id=poll_id))

@app.route('/deletePoll/<poll_id>')
@login_required
def deletePoll(poll_id):
    poll = db.session.query(Poll).filter(Poll.id==poll_id).all()[0]
    db.session.delete(poll)
    db.session.commit()
    flash('You have deleted poll: {}'.format(poll.title))
    
    return redirect(request.referrer) or redirect(url_for('index')) # request.referrer redirects "Back"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/register_new_user', methods=['GET', 'POST'])
def register_new_user():
    if current_user.is_anonymous == True or current_user.is_admin == False:
        flash('You have to be logged in as an admin to access this feature.')
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(user.username + ' has been registered.')
        return redirect(url_for('manage_users'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>',methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    polls = user.polls.order_by(Poll.timestamp.desc()).paginate(
        page, app.config['POLLS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username,page=polls.next_num) if polls.has_next else None
    prev_url = url_for('user', username=user.username,page=polls.prev_num) if polls.has_prev else None
    
    return render_template('user.html', user=user, polls=polls.items, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',form=form)

@app.route('/edit_poll/<poll_id>', methods=['GET', 'POST'])
@login_required
def edit_poll(poll_id):
    form = EditPollForm()
    poll = db.session.query(Poll).filter(Poll.id==poll_id).all()[0]
    if form.validate_on_submit():
        poll.title = form.title.data
        poll.body = form.body.data
        poll.image_url = form.image_url.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_poll', poll_id = poll_id))
    elif request.method == 'GET':
        form.title.data = poll.title
        form.body.data = poll.body
        form.image_url.data = poll.image_url
    return render_template('edit_poll.html', title='Edit Poll', form=form)

@app.route('/edit_option/<poll_id>/<option_id>', methods=['GET', 'POST'])
@login_required
def edit_option(poll_id, option_id):
    edit_option_form = EditOptionForm()
    edit_option = db.session.query(Option).filter(Option.id==option_id).all()[0]
    polls = db.session.query(Poll).filter(Poll.id==poll_id).all()[0]
    options = db.session.query(Option).filter(Option.id_poll==poll_id).all()

    if edit_option_form.validate_on_submit():
        edit_option.body = edit_option_form.body.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('addOption', poll_id = poll_id))
    elif request.method == 'GET':
        edit_option_form.body.data = edit_option.body
    
    return render_template('editOption.html', title='View Poll', 
        edit_option_form=edit_option_form, options=options, 
        polls=polls, edit_option = edit_option)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/explore')
# @login_required
def explore():
    page = request.args.get('page',1,type=int)
    polls = Poll.query.order_by(Poll.timestamp.desc()).paginate(
        page, app.config['POLLS_PER_PAGE'], False)
    next_url = url_for('explore', page=polls.next_num) if polls.has_next else None 
    prev_url = url_for('explore', page=polls.prev_num) if polls.has_prev else None
    return render_template('explore.html', title='Explore', polls=polls.items, next_url=next_url, prev_url=prev_url)

@app.route('/viewPoll/<poll_id>')
# @login_required
def viewPoll(poll_id):
    polls = db.session.query(Poll).filter(Poll.id==poll_id).all()[0]
    # sorts list
    result = db.session.query(Option, func.count(votes.c.id_option).label('total_count')).outerjoin(votes).group_by(Option.id).filter(Option.id_poll==poll_id).order_by('total_count DESC').all()
    # result = db.session.query(Option, func.count(votes.c.id_option).label('total_count')).outerjoin(votes).group_by(Option.id).filter(Option.id_poll==poll_id).order_by('total_count DESC').all()
    options = [i[0] for i in result] # returns only the objects as a list
    
    return render_template('viewPoll.html', title='View Poll', current_user = current_user, options=options, polls=polls)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

from app.forms import ResetPasswordForm

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)