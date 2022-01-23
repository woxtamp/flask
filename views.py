from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import create_access_token
import datetime

from app import app
from validator import validate
from models import User, Post
from schema import USER_CREATE, POST_CREATE


class UserView(MethodView):

    def get(self, user_id):
        user = User.by_id(user_id)
        return jsonify(user.to_dict())

    @validate('json', USER_CREATE)
    def post(self):
        user = User(**request.json)
        user.set_password(request.json['password'])
        user.add()

        expires = datetime.timedelta(days=7)
        access_token = create_access_token(identity=str(user.id), expires_delta=expires)
        return {'token': access_token}, 200


class PostView(MethodView):

    def get(self, post_id):
        post = Post.by_id(post_id)
        return jsonify(post.to_dict())

    @app.route('/api/posts/', methods=['GET', ])
    def get_all(self):
        posts = {}
        post = Post.query.all()
        for item in post:
            posts[item.id] = item.to_dict()
        print(posts)
        return jsonify(posts)

    @jwt_required
    @validate('json', POST_CREATE)
    def post(self):
        post = Post(**request.json)
        post.user_id = get_jwt_identity()
        post.add()
        return jsonify(post.to_dict())

    @jwt_required
    @validate('json', POST_CREATE)
    def put(self, post_id):
        user_id = get_jwt_identity()
        new_post = Post(**request.json)
        post = Post.by_id_user(post_id, user_id)
        for item in post:
            item.title = new_post.title
            item.text = new_post.text
            item.add()
            return jsonify(item.to_dict())

    @jwt_required
    def delete(self, post_id):
        user_id = get_jwt_identity()
        post = Post.by_id_user(post_id, user_id)
        for item in post:
            item.delete()
        return 'deleted successfully', 200


app.add_url_rule('/api/users/<int:user_id>', view_func=UserView.as_view('user_get'), methods=['GET', ])
app.add_url_rule('/api/login/', view_func=UserView.as_view('user_create'), methods=['POST', ])
app.add_url_rule('/api/posts/<int:post_id>', view_func=PostView.as_view('post_get'), methods=['GET', ])
app.add_url_rule('/api/posts/', view_func=PostView.as_view('post_create'), methods=['POST', ])
app.add_url_rule('/api/posts/<int:post_id>', view_func=PostView.as_view('post_delete'), methods=['DELETE', ])
app.add_url_rule('/api/posts/<int:post_id>', view_func=PostView.as_view('post_put'), methods=['PUT', ])