from django.db import models

# The cart app doesn't need its own models — it tracks cart contents in the
# session (see cart/views.py) and looks up real product data from
# product.models.ProductItem. Leave this file empty unless you later switch
# to a database-backed cart (e.g. tied to a logged-in user).