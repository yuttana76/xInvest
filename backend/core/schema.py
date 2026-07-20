import graphene
import stt_fundconnext.schema

class Query(stt_fundconnext.schema.Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
