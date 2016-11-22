# -*- coding: utf-8 -*-
import os
import datetime

from flask import Flask, render_template, redirect, flash, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a secret string'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')  # in linux the address is: sqlite:////...
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['DEBUG'] = True
# app.config['TEMPLATES_AUTO_RELOAD'] = True  # auto reload page

manager = Manager(app)
db = SQLAlchemy(app)


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    location = db.Column(db.Integer, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    #timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    location = db.Column(db.Integer, unique=True)
    items = db.relationship('Item', backref='category', lazy='dynamic')
    #timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class NewItemForm(Form):
    categories = Category.query.all()
    body = StringField(validators=[DataRequired()])
    category = SelectField(choices=[(category.id, category.name) for category in categories])
    submit = SubmitField(u'添加')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NewItemForm()
    if form.validate_on_submit():
        body = form.body.data
        category = Category.query.get_or_404(int(form.category.data))
        item = Item(body=body, category=category)
        db.session.add(item)
        db.session.commit()
    items = Item.query.all()
    categories = Category.query.all()
    return render_template('index.html', items=items, categories=categories, form=form)


@app.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    return render_template('index.html', category=category)


@app.route('/new-category', methods=['GET', 'POST'])
def new_category():
    name = request.form.get('name')
    category = Category(name=name)
    db.session.add(category)
    return redirect(url_for('index'))


@app.route('/edit-item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    item = Item.query.get_or_404(id)
    item.body = request.form.get('body')
    #item.location = request.form.get['i-location']
    # item.category = request.form.get('category', item.category)
    db.session.add(item)
    return redirect(url_for('index'))


@app.route('/edit-category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    category.name = request.form.get('name')
    #category.location = request.form.get['c-location']
    db.session.add(category)
    return redirect(url_for('index'))


@app.route('/delete-item/<int:id>')
def del_item(id):
    item = Item.query.get_or_404(id)
    if item is None:
        flash(u'无效的操作。', 'warning')
    db.session.delete(item)
    db.session.commit()
    flash(u'删除成功。', 'success')
    return redirect(url_for('index'))


@app.route('/delete-category/<int:id>')
def del_category(id):
    category = Category.query.get_or_404(id)
    if category is None:
        flash(u'无效的操作。', 'warning')
    db.session.delete(category)
    db.session.commit()
    flash(u'删除成功。', 'success')
    return redirect(url_for('index'))


@app.route('/setting')
def setting():
    return redirect(url_for('index'))

if __name__ == '__main__':
    manager.run()