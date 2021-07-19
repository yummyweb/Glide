class http:
    def getHandler(self, ctx):
        ctx._log()
        ctx._set_headers({
            'Content-Type': 'application/json'
        })
        ctx.wfile.write(ctx._serialise({
            'message': 'Hello, world!'
        }))