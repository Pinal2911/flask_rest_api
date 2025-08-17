from marshmallow import Schema, fields

#this is from client to API
#this is the requested data

#since it is creation all attributes are required and id is dump_only
class PlainItemSchema(Schema):
    id=fields.Str(dump_only=True)
    name=fields.Str(required=True)
    price=fields.Float(required=True)

class ItemSchema(PlainItemSchema):
    store_id=fields.Integer(required=True)
    store=fields.Nested(PlainItemSchema(),dump_only=True)


#here since it is update it is not mandatory to be changed and hence only two fields are provided
class ItemUpdateSchema(Schema):
    name=fields.Str()
    price=fields.Str()
    store_id=fields.Integer(required=True)
    
#store schema
class PlainStoreSchema(Schema):
    id=fields.Str(dump_only=True)
    name=fields.Str(required=True)

class PlainTagSchema(Schema):
    id=fields.Int(dump_only=True)
    name=fields.Str()

class TagSchema(PlainTagSchema):
    store_id=fields.Int(load_only=True)
    store=fields.Nested(PlainStoreSchema(),dump_only=True)

class StoreSchema(PlainStoreSchema):
    items=fields.List(fields.Nested(PlainItemSchema()))
    tags=fields.List(fields.Nested(PlainTagSchema()))

class TagAndItemSchema(Schema):
    message=fields.Str()
    item=fields.Nested(ItemSchema)
    tag=fields.Nested(TagSchema)

class UserSchema(Schema):
    id=fields.Int(dump_only=True)
    username=fields.Str(required=True)
    #due to load_only, we can never get the password in requests 
    password=fields.Str(required=True,load_only=True)

