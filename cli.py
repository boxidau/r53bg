import boto3
import click
import botocore.exceptions
import sys
import time

@click.command()
@click.argument('zoneid')
@click.argument('fqdn')
@click.argument('from_record_set_id')
@click.argument('to_record_set_id')
@click.option('--rate', help='Rate of weight change per 30 seconds, min 1 max 255, default 10', default=10, type=click.IntRange(1, 255))
def cli(zoneid, fqdn, from_record_set_id, to_record_set_id, rate):
    client = boto3.client('route53')

    click.secho('INFO:\tVerifying Hosted Zone {0}'.format(zoneid), fg='blue')
    # make sure zone exists
    try:
        zone = client.get_hosted_zone(Id=zoneid)
        click.secho('OK:\t\tZone Found - {0}'.format(zone['HostedZone']['Name']), fg='green')
    except botocore.exceptions.ClientError as e:
        click.secho(repr(e), fg='red')
        sys.exit(1)

    # get records
    try:
        records = client.list_resource_record_sets(
            HostedZoneId=zoneid,
            StartRecordName=fqdn,
        )
    except botocore.exceptions.ClientError as e:
        click.secho(repr(e), fg='red')
        sys.exit(1)

    if len(records['ResourceRecordSets']) < 2:
        click.secho('ERROR:\t{0} records found starting with name {1}'.format(
            len(records['ResourceRecordSets']),
            fqdn
        ))
        sys.exit(1)

    click.secho('INFO:\tFinding matching records for {0}'.format(fqdn), fg='blue')
    # filter records to matching exact names
    from_record = None
    to_record = None
    for rec in records['ResourceRecordSets']:
        if rec['Name'] == fqdn:
            try:
                if rec['SetIdentifier'] == from_record_set_id:
                    from_record = rec
                    continue
                if rec['SetIdentifier'] == to_record_set_id:
                    to_record = rec
                    continue
            except KeyError:
                pass
        else:
            pass

    if not from_record:
        click.secho(
            'ERROR:\tSpecified FROM record set identifier {0} could not be found'.format(from_record_set_id),
            fg='red'
        )
        sys.exit(1)

    if not to_record:
        click.secho(
            'ERROR: Specified TO record set identifier {0} could not be found'.format(to_record_set_id),
            fg='red'
        )
        sys.exit(1)

    click.secho('OK:\t\tFound matching records')
    while from_record['Weight'] > 0 or to_record['Weight'] < 255:
        change_applied = False
        from_record['Weight'] -= rate
        to_record['Weight'] += rate

        if from_record['Weight'] < 0:
            from_record['Weight'] = 0

        if to_record['Weight'] > 255:
            to_record['Weight'] = 255

        click.secho('INFO:\tUpdating {0} weight = {1}'.format(from_record['SetIdentifier'], from_record['Weight']))
        click.secho('INFO:\tUpdating {0} weight = {1}'.format(to_record['SetIdentifier'], to_record['Weight']))

        change_response = client.change_resource_record_sets(
            HostedZoneId=zoneid,
            ChangeBatch={
                'Comment': '{0} -> {1}',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': from_record
                    },
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': to_record
                    }
                ]
            }
        )
        # click.secho('INFO:\tWaiting for update to apply', fg='blue')
        #
        # while not change_applied:
        #     time.sleep(30)
        #     response = client.get_change_details(
        #         Id=change_response['ChangeInfo']['Id']
        #     )
        #     print repr(response)
        #     if response['ChangeBatchRecord']['Status'] == 'INSYNC':
        #         change_applied = True
        #         click.secho('INFO:\tUpdate applied', fg='blue')

        # sleep for 30 seconds
        time.sleep(60)

    click.secho('INFO:\t{0} weight = {1}'.format(from_record['SetIdentifier'], from_record['Weight']))
    click.secho('INFO:\t{0} weight = {1}'.format(to_record['SetIdentifier'], to_record['Weight']))
    click.secho('OK:\t\tAll Done!', fg='green')
    sys.exit(0)

if __name__ == "__main__":
    cli()