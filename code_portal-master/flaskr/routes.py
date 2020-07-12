from flask import render_template, flash, redirect, url_for, request, abort
from flaskr import app, db
from flaskr.forms import RegistrationForm, LoginForm, PostForm
from flaskr.models import User, Post, Jobs, Hackathon
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route('/contests')
def display_contests():
    page = request.args.get('page', 1, type=int)
    posts = Post.query\
        .order_by(Post.contest_date.desc()).paginate(page=page, per_page=2)
    return render_template('home.html', title='Contests Page', posts=posts)


@app.route('/jobs')
def display_jobs():
    page = request.args.get('page', 1, type=int)
    jobs = Jobs.query\
        .order_by(Jobs.post_entry_date.inc()).paginate(page=page, per_page=2)
    return render_template('display_jobs.html', title='Jobs Page', posts=jobs)


def display_hackathons():
    page = request.args.get('page', 1, type=int)
    hackathons = Hackathon.query\
        .order_by(Hackathon.contest_date.desc()).paginate(page=page, per_page=2)
    return render_template('display_hackathons.html', title='hackathons Page', posts=hackathons)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        t_user = User.query.filter_by(username=form.username.data).first()
        if t_user and (t_user.pwd == form.password.data):
            login_user(t_user, remember=form.remember.data)
            flash(f'You have been logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page\
                else redirect(url_for('home'))
        else:
            flash(f'Wrong credentials', 'danger')
    return render_template('login.html', title='Login Page', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        temp_user = User(username=form.username.data, pwd=form.password.data, points=0)
        db.session.add(temp_user)
        db.session.commit()
        flash('Account Created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register Page', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

###################### CONTESTS ##########################################################################

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, contest_url=form.url.data,
                    content=form.content.data,
                    author=current_user, contest_date=form.date.data)
        db.session.add(post)
        db.session.commit()
        post.author.points += 5 #contests weightage as 5
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('display_conetests'))
    return render_template('create_post.html',
                           title='New Post', form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.contest_url = form.url.data
        post.content = form.content.data
        post.contest_date = form.date.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.url.data = post.contest_url
        form.date.data = post.contest_date
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('display_contests'))



######################################################################################################################

################################ HACKATHONS #########################################################
@app.route("/hackathon/new", methods=['GET', 'POST'])
@login_required
def new_hackathon():
    form = PostForm()
    if form.validate_on_submit():
        hackathon = Hackathon(title=form.title.data, contest_url=form.url.data,
                    content=form.content.data,
                    author=current_user, contest_date=form.date.data)
        db.session.add(hackathon)
        db.session.commit()
        hackathon.author.points += 5  # contests weightage as 5
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('display_hackathons'))
    return render_template('create_hackathon.html',
                           title='New Post', form=form, legend='New Post')


@app.route("/hackathon/<int:hackaton_id>")
def hackathon(hackathon_id):
    hackathon = Post.query.get_or_404(hackathon_id)
    return render_template('hackathons.html', title=post.title, post=post)


@app.route("/hackathon/<int:hackathon_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    if hackathon.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        hackathon.title = form.title.data
        hackathon.contest_url = form.url.data
        hackathon.content = form.content.data
        hackathon.contest_date = form.date.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('hackathon', hackathon_id=hackathon.id))
    elif request.method == 'GET':
        form.title.data = hackathon.title
        form.content.data = hackathon.content
        form.url.data = hackathon.contest_url
        form.date.data = hackathon.contest_date
    return render_template('create_post.html', title='Update Hackathon',
                           form=form, legend='Update Hackathon')


@app.route("/hackathon/<int:hackathon_id>/delete", methods=['POST'])
@login_required
def delete_post(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    if hackathon.author != current_user:
        abort(403)
    db.session.delete(hackathon)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('display_hackathons'))



######################################################################################################################


################################ JOBS #######################################################################
@app.route("/job/new", methods=['GET', 'POST'])
@login_required
def new_hackathon():
    form = PostForm()
    if form.validate_on_submit():
        job = Jobs(title=form.title.data, contest_url=form.url.data,
                    content=form.content.data,
                    author=current_user, contest_date=form.date.data)
        db.session.add(job)
        db.session.commit()
        job.author.points += 5  # contests weightage as 5
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('display_jobs'))
    return render_template('create_job.html',
                           title='New Post', form=form, legend='New Post')


@app.route("/job/<int:job_id>")
def job(job_id):
    job = Hackathon.query.get_or_404(job_id)
    return render_template('jobs.html', title=post.title, post=post)


@app.route("/job/<int:job_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(job_id):
    job = Jobs.query.get_or_404(job_id)
    if job.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        job.title = form.title.data
        job.contest_url = form.url.data
        job.content = form.content.data
        job.contest_date = form.date.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('job', job_id=job.id))
    elif request.method == 'GET':
        form.title.data = hackathon.title
        form.content.data = hackathon.content
        form.url.data = hackathon.contest_url
        form.date.data = hackathon.contest_date
    return render_template('create_post.html', title='Update Jobs',
                           form=form, legend='Update Jobs')


@app.route("/job/<int:job_id>/delete", methods=['POST'])
@login_required
def delete_job(job_id):
    job = Hackathon.query.get_or_404(job_id)
    if job.author != current_user:
        abort(403)
    db.session.delete(hackathon)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('display_jobs'))



######################################################################################################################


############## user_ka_post ##################################################################
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.contest_date.desc())\
        .paginate(page=page, per_page=2)
    return render_template('user_posts.html', posts=posts, user=user)
