import sys, unittest
sys.path.append('../')
import module.function as fct

class TestFunctions(unittest.TestCase):
    ''' Read data 
    '''
    def test_formatVariation(self):
        self.assertEqual(fct.get_min_bid_index('ShareX', data), 5)
    
    def test_get_max_ask_index(self):
        self.assertEqual(fct.get_max_ask_index('ShareX', data), 0)

if __name__ == '__main__':
    input_file_path = "../input/data.csv"    
    data = fct.load_data(input_file_path)        
    unittest.main()