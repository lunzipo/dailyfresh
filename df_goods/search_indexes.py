from haystack import indexes
from df_goods.models import Goods


# 指定对于某个类的某些数据建立索引
# 类名必须为需要检索的Model_name+Index,这里需要检索goods，所以创建GoodsIndex
class GoodsIndex(indexes.SearchIndex, indexes.Indexable):
    # 创建一个text字段
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):  # 重载get_mode方法，必须要有
        return Goods

    def index_queryset(self, using=None):  # 重载index_函数
        return self.get_model().objects.all()  # 创建所有的索引结果
