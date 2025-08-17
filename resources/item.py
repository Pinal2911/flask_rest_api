import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from schemas import ItemSchema,ItemUpdateSchema
from models import ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from flask_jwt_extended import jwt_required,get_jwt

logger = logging.getLogger(__name__)

blp=Blueprint("Items",__name__,description="Operations on items")

@blp.route("/item/<string:id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200,ItemSchema)
    def get(self,id):
       #this will itself handle if found and. not found error etc
       item=ItemModel.query.get_or_404(id)
       return item

    @jwt_required()
    def delete(self,id):
        jwt=get_jwt()
        if not jwt.get("is_admin"):

            abort(401,message=f"admin privilege requried {jwt.get("is_admin")} {id}")

        item=ItemModel.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "item deleted"},200
        
    @blp.arguments(ItemUpdateSchema)
    #api to client
    @blp.response(200,ItemSchema)
    def put(self,id,item_data):
       item=ItemModel.query.get(id)

       item.price=item_data["price"]
       item.name=item_data["name"]

       db.session.add(item)
       db.session.commit()
       
       return {"message": "item updated"}, 200


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200,ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
    @blp.arguments(ItemSchema)
    @blp.response(201,ItemSchema)
    def post(self,item_data):
        
        item=ItemModel(**item_data)
        
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="An error occurreed while inserting the item")

        return item
