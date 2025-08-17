# import uuid
# from flask import Flask,request
# from db import stores,items
# from flask_smorest import abort
# app=Flask(__name__)

# @app.get('/store')
# def get_store_details():
#     return {'stores' : list(stores.values())},201

# @app.get("/store/<string:store_id>")
# def get_store_by_id(store_id):
#     try:
#         if store_id in stores:
#             return stores[store_id],201
#     except KeyError as e:
#         abort(404,"store not found")

# #create new store
# @app.post("/store")
# def create_store():
#     store_data=request.get_json()
#     if("name" not in store_data):
#         abort(404,"store name not found")
#     for st in stores:
#         if(st["name"] == store_data["name"] ):
#             abort(404,"store already exist")
#     store_id=uuid.uuid4().hex
#     new_store= {**store_data,"id":store_id}
#     stores[store_id]=new_store
#     return new_store,201

# @app.delete("/store/<string:store_id>")
# def delete_store(store_id):
#     try:
#         del stores[store_id]
#         return {"message ": "stored deleted!"}
#     except KeyError:
#         abort(404,message="store not found")

# @app.post("/item")
# def create_item():
#     item_data=request.get_json()
#     if("price" not in item_data or
#        "store_id" not in item_data or
#        "name" not in item_data
#        ):
#         abort(404,"check if store_id, price and name is present as input")
#     for it in items:
#         if item_data["name"] == it["name"] and item_data["store_id"] == "store_data":
#             abort(404,"item already exists")
#     if item_data["store_id"] not in stores:
#        abort(404,"Store not found")
#     item_id=uuid.uuid4().hex
#     item={**item_data,"id":item_id}
#     items[item_id]=item
#     return items,201

# @app.get("/item")
# def get_all_items():
#    return {"items":list(items.values())},201

# @app.get("/item/<string:id>")
# def get_item_by_id(id):
#     try:
#         if id in items:
#             return items[id],201
#     except KeyError:
#         abort(404,"item not found")

# @app.put("/item/<string:id>")
# def update_item(id):
#     item_data=request.get_json()
#     if "name" not in item_data or "price" not in item_data:
#         abort(404,"INVALID DATA")
#     try:
#         item=items[id]
#         item |= item_data

#         return {f"message":"Item updated! {item}"}
#     except KeyError:
#         abort(404,"item not found!")

# @app.delete("/item/<string:id>")
# def delete_item(id):
#     try:
#         del items[id]
#         return {"message":"item deleted!"}
#     except KeyError:
#         abort(404,"item not found")
from flask import Flask
from flask_smorest import Api
from db import db
import models
from resources.store import blp as StoreBlueprint
from resources.item import blp as ItemBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
import logging
from flask_jwt_extended import JWTManager
from flask import jsonify
import secrets
from blocklist import BLOCKLIST
from flask_migrate import Migrate

def create_app(db_url=None):

    app=Flask(__name__)
    
    logger=logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        console=logging.StreamHandler()
        formatter=logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        console.setFormatter(formatter)
        logger.addHandler(console)

    app.config["PROPAGATE_EXCEPTIONS"]=True
    app.config["API_TITLE"]="Stores REST API"
    app.config["API_VERSION"]="v1"
    app.config["OPENAPI_VERSION"]="3.0.3"
    app.config["OPENAPI_URL_PREFIX"]="/"
    app.config["OPENAPI_SWAGGER_UI_PATH"]= "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"]= "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"]=db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
    app.config["PROPAGATE_EXCEPTIONS"]=True
    #genearted below via -> secrets.SystemRandom().getrandbits(128)
    app.config["JWT_SECRET_KEY"]="164445086186260130590020168362307577466"

    db.init_app(app)
    migrate=Migrate(app,db)
    app.logger.info("APP STARTED")
    api=Api(app)
    jwt=JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header,jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header,jwt_payload):
        return(
            jsonify(
                {"description":"the tkoen has been revoked","error":"token revoked"}
            ),
            401
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header,jwt_payload):
        return(
            jsonify(
                {
                    "description":"token is not fresh",
                    "error":"fresh token required",
                }
            ),
            401
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == "1":
            return {"is_admin": True}
        return {"is_admin":False}
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header,jwt_payload):
        return(
            jsonify({"message":"the token has expired","error":"token expired"}),
            401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return(
            jsonify(
                
                {"message":"signature verification failed",
                "error":"invalid token"}
            ),
            401,
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify(
                {"message":"req doesnt contain and access token",
                "error":"authorization required",}
            ),
            401
        )
 

    with app.app_context():
        db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    return app



        
    
