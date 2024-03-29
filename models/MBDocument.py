from datetime import datetime

from controllers.MBMongo import MBMongo
from umongo import Document, fields


@MBMongo.instance.register
class MBDocument(Document):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(MBDocument, self).__init__(*args, **kwargs)

    create_at = fields.DateField(default=datetime.utcnow())
