#!/usr/bin/env python3

from aws_cdk import core

from static_site.static_site_stack import StaticSiteStack, DomainInfo


DOMAINS = [
    DomainInfo(
        domain_name = 'example.com',
        stage = 'prod',
        hosted_zone_id = '<ROUTE53_HOSTED_ZONE_ID',
        cert_arn =  'arn:aws:acm:us-east-1:<account>:certificate/<cert_iD>', #ACM CERT ID to be used to serve the site
    ),
]

app = core.App()
for domain in DOMAINS:
    id = f'{domain.stage}-{domain.domain_name}'.partition('.')[0]
    StaticSiteStack(app, id, domain)

app.synth()
