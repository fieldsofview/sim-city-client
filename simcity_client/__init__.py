from simcity_client import util
from simcity_client import database
from simcity_client import submit
from simcity_client.document import Token
from ConfigParser import NoSectionError
import os

def init():
    try:
        result = {}

        if 'SIMCITY_JOBID' in os.environ:
            result['job_id'] = os.environ['SIMCITY_JOBID']
        
        result['config'] = util.Config()
        couch_cfg = result['config'].section('CouchDB')
        result['database'] = database.CouchDB(
                                        url=couch_cfg['url'],
                                        db=couch_cfg['database'],
                                        username=couch_cfg['username'],
                                        password=couch_cfg['password'])
        return result
    except NoSectionError:
        raise ValueError("Configuration file " + result['config'].filename + "does not contain CouchDB section")
    except IOError as ex:
        raise IOError("Cannot establish connection with CouchDB: " + ex)

def start_job(hostname, database, config):
    host = hostname + '-host'
    host_cfg = config.section(host)
    if host_cfg['method'] == 'ssh':
        submitter = submit.SSHSubmitter(database,
                            host_cfg['host'],
                            jobdir=host_cfg['path'])
    elif host_cfg['method'] == 'osmium':
        submitter = submit.OsmiumSubmitter(database,
                            host_cfg['port'],
                            jobdir=host_cfg['path'])
    else:
        raise ValueError('Host ' + hostname + ' not configured under ' + host + 'section')
    
    submitter.submit([host_cfg['script']])

def add_token(database, properties):
    t = Token(properties)
    return database.save(t)
