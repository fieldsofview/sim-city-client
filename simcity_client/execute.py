import os
from simcity_client.util import listfiles, write_json, Timer, expandfilename
from subprocess import call
import sys

class RunActor(object):
    """Executor class to be overwritten in the client implementation.
    """
    def __init__(self, database):
        """
        @param iterator: the view iterator to get the tokens from.
        """
        self.database = database
    
    def run(self, maxtime=-1):
        """Run method of the actor, executes the application code by iterating
        over the available tokens in CouchDB.
        """
        time = Timer()
        self.prepare_env()
        for token in self.database.token_iterator('todo'):
            self.prepare_run()
            
            try:
                self.process_token(token)
            except Exception as ex:
                msg = "Exception " + str(type(ex)) + " occurred during processing: " + str(ex)
                token.error(msg, exception=ex)
                print msg
            
            self.database.save(token)
            self.cleanup_run()
            
            if maxtime > 0 and time.elapsed() > maxtime:
                    sys.exit(0)
        
        self.cleanup_env()
        
    def prepare_env(self, *kargs, **kwargs):
        """Method to be called to prepare the environment to run the 
        application.
        """
        pass
    
    def prepare_run(self, *kargs, **kwargs):
        """Code to run before a token gets processed. Used e.g. for fetching
        inputs.
        """
        pass
    
    def process_token(self, key, token):
        """The function to overwrite which processes the tokens themselves.
        @param key: the token key. Should not be used to hold anything
        informative as it is mainly used to determine the order in which the
        tokens are returned.
        @param key: the key indicating where the token is stored in the 
        database.
        @param token: the token itself. !WARNING
        """
        raise NotImplementedError

    def cleanup_run(self, *kargs, **kwargs):
        """Code to run after a token has been processed.
        """
        pass
    
    def cleanup_env(self, *kargs, **kwargs):
        """Method which gets called after the run method has completed.
        """
        pass

class ExecuteActor(RunActor):
    def __init__(self, database, config):
        super(ExecuteActor, self).__init__(database)
        self.config = config.section('Execution')
    
    def process_token(self, token):
        print "-----------------------"
        print "Working on token: " + token.id

        dirs = self.create_dirs(token)
        params_file = os.path.join(dirs['input'], 'input.json')
        write_json(params_file, token.input)
        
        token['execute_properties'] = {'dirs': dirs, 'input_file': params_file}
        
        command = [expandfilename(token['command']), dirs['tmp'], dirs['input'], dirs['output']]
        stdout = os.path.join(dirs['output'], 'stdout')
        stderr = os.path.join(dirs['output'], 'stderr')
        try:
            with open(stdout, 'w') as fout, open(stderr, 'w') as ferr:
                returnValue = call(command,stdout=fout, stderr=ferr)
            
            if returnValue != 0:
                token.error("Command failed")
        except Exception as ex:
            token.error("Command raised exception", ex)
        
        token.output = {}

        # create readable standard err/out
        with open(stdout) as fout, open(stderr) as ferr:
            token.output['stdout'] = fout.read()
            token.output['stderr'] = ferr.read()
        
        # Read all files in as base
        out_files = listfiles(dirs['output'])
        for filename in out_files:
            with open(os.path.join(dirs['output'], filename), 'r') as f:
                token.put_attachment(filename, f.read())

        token.mark_done()
        print "-----------------------"
    
    def create_dirs(self, token):
        dir_map = {'tmp': 'tmp_dir', 'input': 'input_dir', 'output': 'output_dir'}
        
        dirs = {}
        for d, conf in dir_map.iteritems():
            superdir = expandfilename(self.config[conf])
            if not os.path.exists(superdir):
                os.mkdir(superdir)
            
            dirs[d] = os.path.join(superdir, token.id + '_' + str(token['lock']))
            os.mkdir(dirs[d])
        
        return dirs
