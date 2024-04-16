import unittest
import os
from oc_meta.run.fixer.prov.add_sources_from_rdf import extract_and_process_json
import shutil
from rdflib import ConjunctiveGraph, URIRef
from rdflib.compare import isomorphic, graph_diff
import zipfile
import json

class TestExtractAndProcessJson(unittest.TestCase):
    def setUp(self):
        # Percorsi per i file zip di sorgente e di destinazione
        self.source_zip_folder = os.path.join('test', 'fixer_tests', 'data', 'source') + os.sep
        self.source_zip_path = os.path.join('test', 'fixer_tests', 'data', 'source', 'br', '0610', '10000', '1000', 'prov', 'se.zip')
        self.destination_zip_path = os.path.join('test', 'fixer_tests', 'data', 'destination', 'br', '0610', '10000', '1000', 'prov', 'se.zip')

        # Percorso temporaneo per evitare modifiche al file originale
        self.temp_destination_zip_path = os.path.join('test', 'fixer_tests', 'data', 'tmp', 'br', '0610', '10000', '1000', 'prov', 'temp_destination.zip')
        
        # Assicurati che i file sorgente e destinazione esistano
        assert os.path.exists(self.source_zip_path)
        assert os.path.exists(self.destination_zip_path)

        # Copia il contenuto del file di destinazione in un file temporaneo
        if os.path.exists(self.temp_destination_zip_path):
            os.remove(self.temp_destination_zip_path)
        shutil.copyfile(self.destination_zip_path, self.temp_destination_zip_path)

    def tearDown(self):
        # Pulizia dopo ogni test
        if os.path.exists(self.temp_destination_zip_path):
            os.remove(self.temp_destination_zip_path)

    def test_extraction_and_modification(self):
        original_graph = self.load_rdf_from_zip(self.source_zip_path)
        extract_and_process_json(self.temp_destination_zip_path, self.source_zip_folder)
        modified_graph = self.load_rdf_from_zip(self.temp_destination_zip_path)
        original_graph.remove((URIRef('https://w3id.org/oc/meta/br/0610897/prov/se/1'), URIRef('http://www.w3.org/ns/prov#hadPrimarySource'), URIRef('https://api.crossref.org/')))
        original_graph.add((URIRef('https://w3id.org/oc/meta/br/0610897/prov/se/1'), URIRef('http://www.w3.org/ns/prov#hadPrimarySource'), URIRef('https://api.crossref.org/snapshots/monthly/2022/12/all.json.tar.gz')))
        self.assertTrue(self.graphs_equal(original_graph, modified_graph))

    def load_rdf_from_zip(self, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zf:
            with zf.open(zf.namelist()[0], 'r') as file:
                data = json.load(file)
                graph = ConjunctiveGraph()
                graph.parse(data=json.dumps(data), format='json-ld')
                return graph

    def graphs_equal(self, graph1, graph2):
        return isomorphic(graph1, graph2)

if __name__ == '__main__':
    unittest.main()
