# from pprint import pprint
import unittest
import boto3
from botocore.exceptions import ClientError
from moto import mock_dynamodb2
from pprint import pprint
import sys
sys.path.insert(1, '../todos/')
import warnings
import time


@mock_dynamodb2
class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<socket.socket.*>") 
        warnings.filterwarnings("ignore", category=DeprecationWarning, message="callable is None.*")
        warnings.filterwarnings("ignore", category=DeprecationWarning, message="Using or importing.*")
        """Create the mock database and table"""
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.uuid = "123e4567-e89b-12d3-a456-426614174000"
        self.text = "Aprender DevOps y Cloud en la UNIR"


        from ToDoCreateTable import create_todo_table
        self.table = create_todo_table(self.dynamodb)
        self.table_local = create_todo_table()

        from todoTable import todoTable
        self.table_handler_a = todoTable()
        self.table_a = self.table_handler_a.create_todo_table()
        self.table_handler_b = todoTable()
        self.table_b = self.table_handler_b.create_todo_table(self.dynamodb)
        
    def tearDown(self):
        """Delete mock database and table after test is run"""
        self.table.delete()
        self.table_local.delete()

        self.table_handler_a.delete_todo_table()
        self.table_handler_b.delete_todo_table(self.dynamodb)
        del self.table_handler_a
        del self.table_handler_b
        
        self.dynamodb = None

    def test_table_exists(self):
        self.assertTrue(self.table)  # check if we got a result
        self.assertTrue(self.table_local)  # check if we got a result

        self.assertTrue(self.table_a)  # check if we got a result
        self.assertTrue(self.table_b)  # check if we got a result
        # check if the table name is 'ToDo'
        self.assertIn('todoTable', self.table.name)
        self.assertIn('todoTable', self.table_local.name)
        self.assertIn('todoTablelocal', self.table_a.name)
        self.assertIn('todoTablelocal', self.table_b.name)
        # pprint(self.table.name)

    def test_put_todo(self):
        # Testing file functions        
        from ToDoPutItem import put_todo
        ## Table local  
        self.assertEqual(200, put_todo(self.text, self.uuid)['ResponseMetadata']['HTTPStatusCode'])
        ## Table mock
        self.assertEqual(200, put_todo(self.text, self.uuid, self.dynamodb)['ResponseMetadata']['HTTPStatusCode'])

        # Testing class todoTable
        ## Table a local
        self.assertEqual(200, self.table_handler_a.put_todo(self.text, self.uuid)['ResponseMetadata']['HTTPStatusCode'])
        ## Table b mock
        self.assertEqual(200, self.table_handler_b.put_todo(self.text, self.uuid, self.dynamodb)['ResponseMetadata']['HTTPStatusCode'])

    def test_put_todo_error(self):
        # Testing file functions
        from ToDoPutItem import put_todo
        ## Table local 
        self.assertRaises(Exception, put_todo("", self.uuid))
        self.assertRaises(Exception, put_todo("", ""))
        self.assertRaises(Exception, put_todo(self.text, ""))
        ## Table mock
        self.assertRaises(Exception, put_todo("", self.uuid, self.dynamodb))
        self.assertRaises(Exception, put_todo("", "", self.dynamodb))
        self.assertRaises(Exception, put_todo(self.text, "", self.dynamodb))
        # Testing class todoTable
        ## Table a local
        self.assertRaises(Exception, self.table_handler_a.put_todo("", self.uuid))
        self.assertRaises(Exception, self.table_handler_a.put_todo("", ""))
        self.assertRaises(Exception, self.table_handler_a.put_todo(self.text, ""))
        ## Table b mock
        self.assertRaises(Exception, self.table_handler_b.put_todo("", self.uuid, self.dynamodb))
        self.assertRaises(Exception, self.table_handler_b.put_todo("", "", self.dynamodb))
        self.assertRaises(Exception, self.table_handler_b.put_todo(self.text, "", self.dynamodb))

    def test_get_todo(self):
        from ToDoGetItem import get_todo
        from ToDoPutItem import put_todo
        
        # Testing file functions
        ## Table local
        put_todo(self.text, self.uuid)
        self.assertEqual(200, get_todo(self.uuid)['ResponseMetadata']['HTTPStatusCode'])
        self.assertEqual(self.text, get_todo(self.uuid)['Item']['text'])
        
        ## Table mock
        put_todo(self.text, self.uuid, self.dynamodb)
        self.assertEqual(200, get_todo(self.uuid, self.dynamodb)['ResponseMetadata']['HTTPStatusCode'])
        self.assertEqual(self.text, get_todo(self.uuid, self.dynamodb)['Item']['text'])

        # Testing class todoTable
        ## Table a local
        self.table_handler_a.put_todo(self.text,self.uuid)
        self.assertEqual(200, self.table_handler_a.get_todo(self.uuid)['ResponseMetadata']['HTTPStatusCode'])
        self.assertEqual(self.text, self.table_handler_a.get_todo(self.uuid)['Item']['text'])
        
        # ## Table b mock
        self.table_handler_b.put_todo(self.text,self.uuid, self.dynamodb)
        self.assertEqual(200, self.table_handler_b.get_todo(self.uuid, self.dynamodb)['ResponseMetadata']['HTTPStatusCode'])
        self.assertEqual(self.text, self.table_handler_b.get_todo(self.uuid, self.dynamodb)['Item']['text'])

    def test_get_todo_error(self):
        from ToDoPutItem import put_todo
        from ToDoGetItem import get_todo
        # Testing file functions
        ## Table local
        put_todo(self.text, self.uuid)
        self.assertRaises(TypeError, get_todo(""))
        # Testing file functions
        ## Table local        put_todo(self.text, self.uuid, self.dynamodb)
        self.assertRaises(TypeError, get_todo("", self.dynamodb))
        # Testing class todoTable
        ## Table a local
        self.table_handler_a.put_todo(self.text,self.uuid)
        self.assertRaises(TypeError, self.table_handler_a.get_todo(""))
        ## Table b mock
        self.table_handler_b.put_todo(self.text,self.uuid, self.dynamodb)
        self.assertRaises(TypeError, self.table_handler_b.get_todo("", self.dynamodb))

    def test_update_todo(self):
        from ToDoPutItem import put_todo
        from ToDoUpdateItem import update_todo
        from ToDoGetItem import get_todo
        updated_text = "Aprender más cosas que DevOps y Cloud en la UNIR"
        # Testing file functions
        ## Table local
        put_todo(self.text, self.uuid)
        self.assertEqual(200, update_todo(updated_text,self.uuid,"false")['ResponseMetadata']['HTTPStatusCode'])
        self.assertEqual(updated_text, get_todo(self.uuid)['Item']['text'])
        ## Table mock
        put_todo(self.text, self.uuid, self.dynamodb)
        self.assertEqual(200, update_todo(updated_text,self.uuid,"false", self.dynamodb)['ResponseMetadata']['HTTPStatusCode'])
        self.assertEqual(updated_text, get_todo(self.uuid, self.dynamodb)['Item']['text'])
        # Testing class todoTable
        ## Table a local
        self.table_handler_a.put_todo(self.text, self.uuid)
        self.assertEqual(200, self.table_handler_a.update_todo(updated_text,self.uuid,"false")['ResponseMetadata']['HTTPStatusCode'])
        self.assertEqual(updated_text, self.table_handler_a.get_todo(self.uuid)['Item']['text'])
        # ## Table b mock
        self.table_handler_b.put_todo(self.text, self.uuid, self.dynamodb)
        self.assertEqual(200, self.table_handler_b.update_todo(updated_text,self.uuid,"false", self.dynamodb)['ResponseMetadata']['HTTPStatusCode'])
        self.assertEqual(updated_text, self.table_handler_b.get_todo(self.uuid, self.dynamodb)['Item']['text'])

    def test_update_todo_error(self):
        from ToDoPutItem import put_todo
        from ToDoUpdateItem import update_todo
        updated_text = "Aprender más cosas que DevOps y Cloud en la UNIR"
        # Testing file functions
        ## Table local
        put_todo(self.text, self.uuid)
        self.assertRaises(Exception, update_todo(updated_text,"","false"))
        self.assertRaises(TypeError, update_todo("", self.uuid,"false"))
        self.assertRaises(Exception, update_todo(updated_text,self.uuid,""))
        ## Table mock
        put_todo(self.text, self.uuid, self.dynamodb)
        self.assertRaises(Exception, update_todo(updated_text,"","false", self.dynamodb))
        self.assertRaises(TypeError, update_todo("", self.uuid,"false", self.dynamodb))
        self.assertRaises(Exception, update_todo(updated_text,self.uuid,"", self.dynamodb))
        # Testing class todoTable
        ## Table a local
        self.table_handler_a.put_todo(self.text, self.uuid)
        self.assertRaises(Exception, self.table_handler_a.update_todo(updated_text,"","false"))
        self.assertRaises(TypeError, self.table_handler_a.update_todo("", self.uuid,"false"))
        self.assertRaises(Exception, self.table_handler_a.update_todo(updated_text,self.uuid,""))
        ## Table b mock
        self.table_handler_b.put_todo(self.text, self.uuid, self.dynamodb)
        self.assertRaises(Exception, self.table_handler_b.update_todo(updated_text,"","false", self.dynamodb))
        self.assertRaises(TypeError, self.table_handler_b.update_todo("", self.uuid,"false", self.dynamodb))
        self.assertRaises(Exception, self.table_handler_b.update_todo(updated_text,self.uuid,"", self.dynamodb))
    
    def test_delete_todo(self):
        from ToDoDeleteItem import delete_todo
        from ToDoPutItem import put_todo
        from ToDoGetItem import get_todo
        
        # Testing file functions
        ## Table local
        put_todo(self.text, self.uuid)
        self.assertEqual(200, delete_todo(self.uuid)['ResponseMetadata']['HTTPStatusCode'])
        
        ## Table mock
        put_todo(self.text, self.uuid, self.dynamodb)
        self.assertEqual(200, delete_todo(self.uuid, self.dynamodb)['ResponseMetadata']['HTTPStatusCode'])
        # self.assertEqual(self.text, get_todo(self.uuid, self.dynamodb)['Item']['text'])

        # Testing class todoTable
        ## Table a local
        self.table_handler_a.put_todo(self.text,self.uuid)
        self.assertEqual(200, self.table_handler_a.delete_todo(self.uuid)['ResponseMetadata']['HTTPStatusCode'])
        # self.assertEqual(self.text, self.table_handler_a.get_todo(self.uuid)['Item']['text'])
        
        # ## Table b mock
        self.table_handler_b.put_todo(self.text,self.uuid, self.dynamodb)
        self.assertEqual(200, self.table_handler_b.delete_todo(self.uuid, self.dynamodb)['ResponseMetadata']['HTTPStatusCode'])
        # self.assertEqual(self.text, self.table_handler_b.get_todo(self.uuid, self.dynamodb)['Item']['text'])    
    
    def test_python_files(self):
        import ToDoPutItem 
        import ToDoGetItem
        import ToDoUpdateItem


        result = ToDoPutItem.main()
        self.assertEqual(200, result['ResponseMetadata']['HTTPStatusCode'])

        result = ToDoGetItem.main()
        self.assertEqual(200, result['ResponseMetadata']['HTTPStatusCode'])

        result = ToDoUpdateItem.main()
        self.assertEqual(200, result['ResponseMetadata']['HTTPStatusCode'])


if __name__ == '__main__':
    unittest.main()
