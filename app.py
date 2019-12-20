#!/usr/bin/env python3

from aws_cdk import core

from static_site.static_site_stack import StaticSiteStack


app = core.App()
StaticSiteStack(app, "static-site")

app.synth()
