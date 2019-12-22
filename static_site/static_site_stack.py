from aws_cdk import (
    aws_cloudfront as cf,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    core
)
from typing import NamedTuple


class DomainInfo(NamedTuple):
    """Domain info to be passed into a Static site stack"""
    domain_name: str
    stage: str
    hosted_zone_id: str
    cert_arn: str


class StaticSiteStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, domain: DomainInfo, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        if domain.stage == 'prod':
            self.final_domain = domain.domain_name
        else:
            self.final_domain = f'{domain.stage}.{domain.domain_name}'
        self.domain = domain

        # Create the static site website bucket
        bucket = s3.Bucket(self, "sitebucket", bucket_name=self.final_domain, public_read_access=True, website_index_document="index.html")
        core.CfnOutput(self, 'site_bucket_name', value=bucket.bucket_name)
        core.CfnOutput(self, 'site_bucket_website', value=bucket.bucket_website_url)

        #create Cloudfront distribution return dist ID
        alias_configuration = cf.AliasConfiguration(
            acm_cert_ref=self.domain.cert_arn,
            names=[self.final_domain],
        )
        source_configuration = cf.SourceConfiguration(
            s3_origin_source=cf.S3OriginConfig(
                s3_bucket_source=bucket,
            ),
            behaviors=[cf.Behavior(is_default_behavior=True)]
        )
        dist = cf.CloudFrontWebDistribution(
            self,
            'staticsitecf',
            alias_configuration = alias_configuration,
            origin_configs =[source_configuration],
        )
        core.CfnOutput(self, 'static_site_cf_dist_id', value=dist.distribution_id)
        core.CfnOutput(self, 'static_site_cf_domain', value=dist.domain_name)
        
        #route53 logic
        if self.domain.stage == 'prod':
            zone = route53.HostedZone.from_hosted_zone_attributes(
                self,
                id="HostedZoneID",
                hosted_zone_id=self.domain.hosted_zone_id,
                zone_name=self.domain.domain_name
                )
            route53.ARecord(
                self,
                'SiteAliasRecord',
                record_name=self.final_domain,
                target=route53.AddressRecordTarget.from_alias(targets.CloudFrontTarget(dist)),
                zone=zone
            )
    
