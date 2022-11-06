from pathlib import Path
import re
import sys

def get_resource_db(provider_file='internal/provider/provider.go'):
        with open(provider_file) as f:
                db = [l.strip() for l in f.readlines() if re.match(r'(?!.*\.DataSource.*)^\s+?"aws_[^_][^"]+":', l)]
        return db

def filter_existing_files(possible_files):
        result = list()
        for prefix in possible_files:
                for ending in (".html.markdown", ".markdown"):
                        f = Path(prefix + ending)
                        if f.exists():
                                result.append(str(f))
                                break
        return list(sorted(result, key=len))

def get_doc_file_name_possibility(resource_db, service, resource):

        file_pattern = './website/docs/r/%s_%s'
        single_file_pattern = './website/docs/r/%s'
        if service == resource:
                return [single_file_pattern % (resource)]

        items = [i.split('"')[1] for i in resource_db if service+"." in i and "_"+resource+'"' in i]
        pattern = r'^aws_(?P<service>.*?)_' + resource + r'$'

        possible_files = list()
        for item in items:
                m = re.match(pattern, item)
                if not m:
                        if service == "ec2":
                                possible_files.append(
                                        file_pattern % (service, resource),
                                )
                                possible_files.append(
                                        single_file_pattern % (resource),
                                )
                                continue
                assert m, f"Didn't find a match: service={service} resouce={resource} item={item} items={items}"

                discovered_service = m.groupdict().get('service')
                possible_files.append(file_pattern % (discovered_service, resource))

        return possible_files


RESOURCE_EXCEPTIONS = {
        ('ec2', 'outposts_local_gateway_route_table_vpc_association'): ["./website/docs/r/ec2_local_gateway_route_table_vpc_association"],
        ('ec2', 'vpc_managed_prefix_list'): ["./website/docs/r/ec2_managed_prefix_list"],
        ('ec2', 'vpc_network_insights_path'): ["./website/docs/r/ec2_network_insights_path"],
        ('ec2', 'vpc_network_insights_analysis'): ["./website/docs/r/ec2_network_insights_analysis"],
        ('ec2', 'vpc_traffic_mirror_filter'): ["./website/docs/r/ec2_traffic_mirror_filter"],
        ('ec2', 'vpc_traffic_mirror_session'): ["./website/docs/r/ec2_traffic_mirror_session"],
        ('ec2', 'vpc_traffic_mirror_target'): ["./website/docs/r/ec2_traffic_mirror_target"],
        ('ec2', 'vpnclient_endpoint'): ["./website/docs/r/ec2_client_vpn_endpoint"],
        ('ec2', 'vpnsite_connection'): ["./website/docs/r/vpn_connection"],
        ('ec2', 'vpnsite_customer_gateway'): ["./website/docs/r/customer_gateway"],
        ('ec2', 'vpnsite_gateway'): ["./website/docs/r/vpn_gateway"],
        ('ec2', 'wavelength_carrier_gateway'): ["./website/docs/r/ec2_carrier_gateway"],
        ('fsx', 'ontap_storage_virtual_machine_migrate'): {"./website/docs/r/fsx_ontap_storage_virtual_machine"},
        ('elb', 'load_balancer'): ["./website/docs/r/elb"],
        ('elbv2', 'load_balancer'): ["./website/docs/r/lb"],
        ('codepipeline', 'webhook'): ["./website/docs/r/codepipeline_webhook"],
}
def get_doc_file_static_exception(service, resource):
        result = RESOURCE_EXCEPTIONS.get((service,resource), [])
        if result:
                return result
        elif service == "ec2":
                if "transitgateway" in resource:
                        resource = resource.replace("transitgateway", "transit_gateway")
                        return  ["./website/docs/r/{}_{}".format(service,resource)]
                if "vpc_default" in resource:
                        resource = resource.replace("vpc_", "", 1)
                        return ["./website/docs/r/{}".format(resource)]
                if resource.startswith('vpc_'):
                        resource = resource.replace("vpc_", "", 1)
                        return ["./website/docs/r/{}".format(resource)]


                resource = resource.replace("ec2_", "")
                return ["./website/docs/r/{}".format(resource)]
        else:
                return []

def parse_service_and_resource(filename):
        pattern = r'.*?\/service\/(?P<service>[^\/]+)\/(?P<resource>[^\/]+).go$'
        m = re.match(pattern, filename)
        groups = m.groupdict()
        return groups.get('service'), groups.get('resource').rstrip('_')

def main():
        files = [line.strip() for line in sys.stdin]

        resource_db = get_resource_db()

        for file in files:
                service, resource = parse_service_and_resource(file)
                file_prefixes = get_doc_file_name_possibility(resource_db, service, resource)
                if not file_prefixes:
                        file_prefixes = get_doc_file_static_exception(service, resource)
                possible_doc_files = filter_existing_files(file_prefixes)

                # Catch errors
                if not possible_doc_files:
                        raise Exception(f"No Possibility service={service} resource={resource} file={file} possible_doc_files={possible_doc_files} perm={possible_doc_files}")

                doc_file = possible_doc_files[0]
                with open(doc_file) as f:
                        has_tags = [line for line in f.readlines() if re.match(r"^\S+\s+`tags`", line)]
                        if not has_tags:
                                print(f"Tags Not Supported: doc_file={doc_file} file={file} service={service} resource={resource}")

if __name__ == '__main__':
        main()
