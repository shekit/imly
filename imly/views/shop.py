from plata.shop.views import Shop

class ImlyShop(Shop):

    def get_context(self, request, context, **kwargs):
        """
        Helper method returning a context dict. Override this if you
        need additional context variables.
        """
        self.ctx = {
            'base_template': self.base_template,
            }
        self.ctx.update(context)
        self.ctx.update(kwargs)
        return self.ctx