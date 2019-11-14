#// Provides helper classes for the database models stored in models.py
from flask import session,current_app
from app.models import *
from collections import namedtuple
from sqlalchemy import func
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import Integer
from app.utils.formatmsg import msg_to_json
import random,colorsys
import json

#// ------------------------------------------------------ Dynamic Query Helper ------------------------------------------------------
class DynamicQuery():
    '''
    .Description: Helper function to generate queries in sqlalchemy
    .Example:
        query = DynamicQuery(
            model_class="dbBlacklist", --> databaseClass (M)
            request_args=[], --> parse request.args for parameters (from a uri string)
            filter=[("id", 'eq', 1),("datatype", 'eq', "path"),("date_added","gt","2018-05-10 02:05:57.1913")], --> filter to apply
            groupby=[("datatype","count"),("datavalue","group")], --> groupby fields
            orderby=("id","desc"),
            getfirst=False, --> return the first record, a lot faster than sorting and limiting on large datasets
            getcount=False, --> return the count record
            as_query=False, --> return the raw query
            as_object=False, --> return the results as an object
            as_datatables=False, --> return the results in datatables form
            as_chartjs=False, --> return the results in chartjs form
            as_schema=False, --> return the schema of a table
            crud=action, --> perform CRUD ops
            data=data, --> data to be used for CRUD (dictionary required, collect with: "data=request.get_json(silent=True)" )
            qjson=data, --> send a query formatted as json (dictionary required, collect with: "qjson=request.get_json(silent=True)" ) # BETA
            inc_fields=["username","id"], --> fields to include in the response
            exc_fields=["password"], --> fields to exclude in the response
            limit=5 --> limit the results
        )
        query.generate().all()
    '''
    def __init__(self, model, access_id=0, request_args=[], filter=[], groupby=[], orderby=(), inc_fields=[], exc_fields=[],
        data={}, qjson={},getfirst=False, getcount=False, as_query=False, as_object=True, as_datatables=False, as_chartjs=False, as_schema=False, crud=None, limit=10):
        '''
        .Description --> Initialize variables, model is required
        '''
        self.access_id = int(access_id)
        self.request_args = request_args
        self.filter = filter
        self.groupby = groupby
        self.orderby = orderby
        self.getfirst = getfirst
        self.getcount = getcount
        self.crud = crud
        self.data = data
        self.qjson = qjson
        self.inc_fields = inc_fields
        self.exc_fields = exc_fields
        self.as_query = as_query
        self.as_object = as_object
        self.as_datatables = as_datatables
        self.as_chartjs = as_chartjs
        self.as_schema = as_schema
        self.limit = limit

        #// Parse request.args from uri string
        if request_args:
            self.parse_uri(request_args)

        #// If grouping fields, get key names
        if self.groupby:
            key_names = dict(self.groupby).keys()
            key_names.insert(0,"count")
            self.groupby_cols = key_names

        #// Get Database Model
        model=model.lower()
        model_record = self.all_models(model)
        self.model = model_record[model]
        self.restricted_attr = model_record["restricted"]
        self.read = model_record["rights"].get("r")
        self.write = model_record["rights"].get("w")

    def all_models(self,model):
        '''
        .Description --> Database model mapping
        .restricted --> these fields will not be returned
        .access --> authenticated user must have their access field equal or above this value
        '''
        model_dict = [
            {"dbuser":dbUser,"restricted":["password_hash"],"rights":{"r":1,"w":4}},
            {"dbagent":dbAgent,"restricted":[],"rights":{"r":1,"w":4}},
            {"dbagenthost":dbAgentHost,"restricted":[],"rights":{"r":1,"w":4}},
            {"dbblacklist":dbBlacklist, "restricted":[],"rights":{"r":1,"w":4}},
            {"dbwhitelist":dbWhitelist, "restricted":[],"rights":{"r":1,"w":4}},
            {"dbaudit":dbAudit, "restricted":[],"rights":{"r":1,"w":4}},
            {"dbtask":dbTask, "restricted":[],"rights":{"r":1,"w":4}},
            {"dbagenthostinteract":dbAgentHostInteract, "restricted":[],"rights":{"r":1,"w":1}},
            {"testtable":TestTable, "restricted":[],"rights":{"r":1,"w":1}},
        ]
        for record in model_dict:
            if model in record:
                return record
        #// If not found in dict, restrict access
        return {str(model):False,"restricted":[],"rights":{"r":None,"w":None}}

    def getelement(self, li, index, default=None):
        '''
        .Description --> Easily get a list element
        '''
        try:
            return li[index]
        except IndexError:
            return default

    def str2bool(self,v):
        '''
        .Description --> Convert string to bool
        .data --> str2bool("true")
        '''
        return str(v).lower() in ("true")

    def parse_uri(self,request):
        '''
        .Description --> Parse request.args and turn into usable parameters.
            Any parameters set explicitly in DynamicQuery() will override request.args
        '''
        for key,value in request.items():
            if key == "filter" and value and not self.filter:
                filter_list = []
                for tup in value.split(";"):
                    filter_list.append(tuple(tup.split(",")))
                self.filter = filter_list
            elif key == "groupby" and value and not self.groupby:
                group_list = []
                for tup in value.split(";"):
                    group_list.append(tuple(tup.split(",")))
                self.groupby = group_list
            elif key == "orderby" and value and not self.orderby:
                self.orderby = tuple(value.split(","))
            elif key == "getfirst" and value and not self.getfirst:
                self.getfirst = self.str2bool(value)
            elif key == "getcount" and value and not self.getcount:
                self.getcount = self.str2bool(value)
            elif key == "inc_fields" and value and not self.inc_fields:
                self.inc_fields = value.split(",")
            elif key == "exc_fields" and value and not self.exc_fields:
                self.exc_fields = value.split(",")
            elif key == "limit" and value != 10:
                self.limit = value
            elif key == "as_datatables" and value and not self.as_datatables:
                self.as_datatables = self.str2bool(value)
            elif key == "as_chartjs" and value and not self.as_chartjs:
                self.as_chartjs = self.str2bool(value)
            elif key == "as_object" and value and not self.as_object:
                self.as_object = self.str2bool(value)
            elif key == "as_query" and value and not self.as_query:
                self.as_query = self.str2bool(value)
            elif key == "as_schema" and value and not self.as_schema:
                self.as_schema = self.str2bool(value)
            elif key == "crud" and value and not self.crud:
                self.crud = value

    def filter_fields(self, data):
        '''
        .Description --> Cut down dictionary based on Include/Exclude and Restricted fields names
        .data -> [{},{}]
        '''
        if not isinstance(data,list):
            data = [data]
        dataset = []
        if self.groupby: #// data is list of tuples
            for tup in data:
                temp_dic = {}
                for count,field in enumerate(tup):
                    key = self.groupby_cols[count]
                    if key not in self.restricted_attr and key not in self.exc_fields:
                        temp_dic[self.groupby_cols[count]] = str(field)
                dataset.append(temp_dic)
        else:
          for record in data: #// data is a sqlalchemy object
            temp_dict = {}
            del record.__dict__["_sa_instance_state"]
            for key,value in record.__dict__.items():
                if key not in self.restricted_attr and key not in self.exc_fields:
                    if not self.inc_fields:
                        temp_dict[key] = value
                    elif key in self.inc_fields:
                        temp_dict[key] = value
            dataset.append(temp_dict)
        return dataset

    def parse_groupby(self):
        '''
        .Description --> Filter for groupby queries
        .data -> [(),()]
        '''
        base_fields = [] #// base fields
        group_fields = [] #// group_by fields
        for tup in self.groupby:
            field ,op = tup
            attr = getattr(self.model,field)
            if "count" in op:
                base_fields.append(func.count(attr))
            group_fields.append(attr)
            base_fields.append(attr)
        return base_fields,group_fields

    def parse_orderby(self,data): #// State: currently sqlalchemy orderby is used instead
        '''
        .Description --> Filter for orderby queries
        .data -> [{},{}]
        '''
        sort_field = self.getelement(self.orderby, 0, None)
        sort_type = self.getelement(self.orderby, 1, None)
        reverse = {"reverse":False}

        if sort_type == "desc":
            reverse["reverse"] = True
        if any(sort_field in d for d in data):
            data = sorted(data, key=lambda k: k[sort_field],**reverse)
        return data

    def to_schema(self):
        '''
        .Description --> Return the columns a table
        '''
        col_list = []
        for col in self.model.__table__.columns:
            if col.key not in self.restricted_attr and col.key not in self.exc_fields:
                if not self.inc_fields:
                    col_list.append(str(col.key))
                elif col.key in self.inc_fields:
                    col_list.append(str(col.key))
        return col_list

    def to_object(self,data):
        '''
        .Description --> Turn data into object
        .data -> [{},{}]
        '''
        dataset = {"data":[],"count":0}
        for record in data:
            dataset["count"] += 1
            dataset["data"].append(namedtuple("Data", record.keys())(*record.values()))
        return dataset

    def to_datatables(self,data):
        '''
        .Description --> Turn data into datatables graph format
        .data -> [{},{}]
        '''
        data_dict = {"draw":0,"data": [],"count":0}
        for record in data:
            data_dict["count"] += 1
            temp_list = []
            if self.groupby:
                include_fields = self.groupby_cols
            elif self.inc_fields:
                include_fields = self.inc_fields
            else:
                include_fields = self.to_schema()
            for field in include_fields:
                try:
                    temp_list.append(record[field])
                except KeyError:
                    print "key: {%s} does not exist or restricted" % (field)
            data_dict["data"].append(temp_list)
        return data_dict

    def to_chartjs(self,data):
        '''
        .Description --> Turn data into chartjs graph format
        .Depends on groupby (mostly)
        .data -> [{},{}]
        '''
        dataset = {"count":0, "label":[], "data": [], "color": []}
        chart_label = []
        chart_data = []
        for record in data:
            h,s,l = random.random(), 0.3 + random.random()/2.0, 0.4 + random.random()/5.0
            r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
            color = "rgb(%s,%s,%s)" % (r,g,b)
            dataset["color"].append(color)

            dataset["count"] += 1
            for k,v in record.items():
                if k == "count":
                    dataset["data"].append(v)
                else:
                    dataset["label"].append(v)
        return dataset

    def to_crud(self,query):
        '''
        .Description --> Perform CRUD operation
        '''
        crud_list = ["insert","update","delete"]
        if self.crud  in crud_list:
            cols = self.to_schema()
            if self.crud == "insert":
                if self.model.__name__ == "dbUser":
                    return dbUser().create_user(self.data)
                else:
                    record = self.model()
                    for k,v in self.data.items():
                        setattr(record,k,v)
                    db.session.add(record)
                    db.session.commit()
                    return msg_to_json("Insert Success.",True,"success")
            elif self.crud == "update":
                if self.data:
                    for k,v in self.data.items():
                        if k not in cols:
                            return msg_to_json("Invalid column data.")
                    query = query.update(self.data)
                    db.session.commit()
                    return msg_to_json("Update Success.",True,"success")
                return msg_to_json("Missing column data.")
            elif self.crud == "delete":
                query = query.delete()
                db.session.commit()
                return msg_to_json("Delete Success.",True,"success")
        return msg_to_json("Invalid CRUD operation.")

    def filter_ops(self, filter_condition):
        '''
        Return filtered queryset based on condition.
        :param query: takes query
        :param filter_condition: Its a list, ie: [(key,operator,value)]
        operator list:
            eq for ==
            lt for <
            ge for >=
            in for in_
            like for like
            value could be list or a string
        :return: queryset
        '''
        if self.groupby: #// Apply any grouping
                base_fields,group_fields = self.parse_groupby()
                __query = db.session.query(*base_fields)
                __query = __query.group_by(*group_fields)
        else:
            __query = db.session.query(self.model)
        for raw in filter_condition:
            try:
                key, op, value = raw
            except ValueError:
                raise Exception('Invalid filter: %s' % raw)

            column = getattr(self.model, key, None)
            if not column:
                raise Exception('Invalid filter column: %s' % key)
            if op == 'in':
                if isinstance(value, list):
                    filt = column.in_(value)
                else:
                    filt = column.in_(value.split(','))
            else:
                try:
                    attr = list(filter(lambda e: hasattr(column, e % op), ['%s', '%s_', '__%s__']))[0] % op
                except IndexError:
                    raise Exception('Invalid filter operator: %s' % op)
                if value == 'null':
                    value = None
                filt = getattr(column, attr)(value)
            __query = __query.filter(filt)
        if self.orderby:
            sort_field = self.getelement(self.orderby, 0, None)
            sort_type = self.getelement(self.orderby, 1, None)
            if sort_type == "desc":
                q = getattr(self.model,sort_field).desc()
            elif sort_type == "asc":
                q = getattr(self.model,sort_field).asc()
            __query = __query.order_by(q)
#        if True: #// must include fields from orderby
#            __query = __query.distinct(getattr(self.model,"id"))
#            __query = __query.distinct(getattr(self.model,"cmd"))

        #// Query on JSON fields
        if self.qjson:
            __query = self.json_query(__query)
        return __query

    def json_query(self,queryobj):
        '''
        :Description - Query for data in JSON format (can query fields stored in JSON and `indexed` fields as well)
        :For JSON fields - Need to specifiy string in `subkeys`
        :For indexed fields - Leave `subkeys` as a empty array
        :Usage - {"query": {
                     "or_": [
                       {"column":"data","subkeys":["category"],"op":"eq","value":"win32_computersystemA"}, # will search column with JSON
                       {"column":"id","subkeys":[],"op":"eq","value":"indexed field"}, # will search indexed column
                     ],
                     "must_":[
                       {"column":"data","subkeys":["category"],"op":"eq","value":"win32_computersystemcoB"},
                     ],
                     "not_": [
                       {"column":"data","subkeys":["category"],"op":"eq","value":"win32_computersystemcoB"},
                     ]
                   }
                 }
        '''
        list_map = {
            "or_":{"args":[],"op":or_},
            "must_":{"args":[],"op":and_},
            "not_":{"args":[],"op":not_}
        }
        query = queryobj
        if not self.qjson: #// If there is not a query object request, return.
            return query
        try:
            for op_list,queries in self.qjson.get("query",None).items():
                if queries:
                    for data in queries:
                        try:
                            column = data["column"]
                            subkeys = data.get("subkeys",None)
                            op = data.get("op","eq")
                            value = data["value"]
                        except ValueError:
                            raise Exception('Invalid filter. Column and Value are mandatory.')

                        filt = getattr(self.model, column, None)
                        if not filt:
                            raise Exception('Invalid filter column: %s' % column)

                        if subkeys:
                            filt = filt[(subkeys)].astext
                            if isinstance(value, int):
                                filt = filt.cast(Integer)

                        if op == 'in':
                            if isinstance(value, list):
                                filt = filt.in_(value)
                            else:
                                filt = filt.in_(value.split(','))
                        else:
                            try:
                                attr = list(filter(lambda e: hasattr(filt, e % op), ['%s', '%s_', '__%s__']))[0] % op
                            except IndexError:
                                raise Exception('Invalid filter operator: %s' % op)

                            filt = getattr(filt, attr)(value)

                        list_map[op_list]["args"].append(filt)

            #// Add or_,not_,and_ to the query
            if list_map["not_"]["args"]:
                for each_not in list_map["not_"]["args"]:
                    query = query.filter(not_(each_not))

            query = query.filter(
                or_(
                    and_(
                        *list_map["must_"]["args"]
                    ),
                    *list_map["or_"]["args"]
                ),
            )
            # Backup
            #for op, attr in list_map.items():
            #    if attr["args"]:
            #        query = query.filter(attr["op"](*attr["args"]))

        except Exception as e:
            print str(e)
        finally:
            return query

    def generate(self):
        '''
        .Description --> Generate a query and CRUD ops
        .data -> [{},{}]
        '''
        try:
            dataset = []

            if self.access_id < self.read or self.read is None:
                raise Exception("User does not have Read access.")

            if self.model is False:
                raise Exception("Database Model does not exist.")

            #// Return schema of table
            if self.as_schema:
                return self.to_schema()

            #// Filter query by sending to filter_ops functions
            query = self.filter_ops(self.filter)

            #// CRUD Operations
            if self.crud is not None:
                if self.access_id < self.write:
                    raise Exception("User does not have Write access.")
                return self.to_crud(query)

            total_count = query.count()
            #// Set record limit
            if self.limit:
                query = query.limit(self.limit)

            #// Return query
            if self.as_query is True:
                return query

            #// Return data (with filter applied)
            else:
                #// Return count
                if self.getcount is True:
                    data_dict = {"data": [],"count":total_count,"total":total_count}
                    return data_dict
                #// One record
                elif self.getfirst is True:
                    raw_data = query.first()
                else: #// Get all
                    raw_data = query.all()
                data = self.filter_fields(raw_data)

#                if self.orderby:
#                    data = self.parse_orderby(data)

                #// Specify the format
                if self.as_datatables:
                    dataset = self.to_datatables(data)
                elif self.as_chartjs:
                    dataset = self.to_chartjs(data)
                elif self.as_object:
                    dataset = self.to_object(data)
                dataset["total"] = total_count
                return dataset
        except Exception as e:
            return msg_to_json(e)
