import rdflib
from rdflib.plugins.sparql import prepareQuery


class Question:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer


# an instance is a tuple with a SPARQL-query and related questions that are answered by the query
class Instance:

    # initialized with empty variables
    def __init__(self):
        self.query = ""
        self.questions = []
        self.variables = []
        self.temp = ""

    # sets the question variable
    def set_query(self, query):
        self.query = query
        return

    # adds a question to the list of questions
    def add_question(self, question):
        self.questions.append(question)
        return

    def add_variable(self, var):
        self.variables.append(var)
        return

    def set_temp_variables(self, vars):
        self.temp = vars
        return


# this method is responsible for initiating the program with a config file
def intialize_system(config):
    # all instances are saved here
    instances = []

    # the Config-File is separated in words
    config = str(config).split()

    # counter to identify which current instance is analyzed
    instance_counter = 0

    # booleans which type of entry is read at the moment
    query = False
    question = False
    variables = False

    # the string can be either a question or query, which is iteratively completed and resets with keywords
    string = ""

    # loop for every word in the config file
    for word in config:

        # keyword INSTANCE creates an instance and increments the counter
        if word == "<INSTANCE>":
            instances.append(Instance())
            instance_counter = instance_counter + 1

        # keyword /QUERY : the resulting query is added to the instance
        if word == "</QUERY>":
            instances[instance_counter - 1].set_query(string)
            query = False
            string = ""

        # keyword /QUESTION : the resulting question is added to the instance
        if word == "</QUESTION>":
            instances[instance_counter - 1].add_question(string)
            question = False
            string = ""

        # keyword /VARIABLES
        if word == "</VARIABLES>":
            instances[instance_counter - 1].set_temp_variables(string)
            variables = False
            string = ""

        # the string is iteratively completed and delimited by spaces
        if query or question or variables:
            string = string + word + " "

        if word == "<QUERY>":
            query = True

        if word == "<QUESTION>":
            question = True

        if word == "<VARIABLES>":
            variables = True

    return instances


# has to be ttl file
def initialize_graph(filename):
    # creates the graph
    g = rdflib.Graph()

    # loads the graph with ttl ontology
    g.load(filename, format="ttl")

    return g


def print_all_instances(instances, graph):
    for instance in instances:
        for question in instance.questions:
            print(question + ":")
            for row in graph.query(instance.query):
                print(row.d)


def separate_variables(instance):
    i = 0
    vars_len = len(instance.temp)
    current = ""

    while i < vars_len:

        if instance.temp[i] == " " and current != "":
            instance.add_variable(current)
            current = ""

        else:
            current = current + instance.temp[i]

        i = i + 1


def bind_var_to_question(question, var, new):
    if new:
        return str(question).replace(var, new)
    else:
        # return None
        return str(question).replace(var, var)


def main():
    # All Questions are stored here
    result = []

    # reads the config file
    config_file = open("my_config.txt", "r")

    # creates the instances given in confiq file
    instances = intialize_system(config_file.read())

    # initializes the graph for the ontology
    # ontology = "untitled-ontology-14"
    ontology = "spanish_law"
    g = initialize_graph(ontology)

    # + " " because that is generated automatically
    # question = input("Ask a question:\n") + " "

    for instance in instances:
        separate_variables(instance)

    for instance in instances:
        for question in instance.questions:
            for row in g.query(instance.query):
                i = 0
                q = question

                for var in instance.variables:
                    q = bind_var_to_question(q, var, row[i])

                    i = i + 1
                if "?" not in q:
                    q = q + "?"
                    result.append(Question(q, row[i]))

    # for instance in instances:
    #     for question in instance.questions:
    #         for row in g.query(instance.query):
    #             i = 0
    #             variables_amount = len(instance.variables)
    #             q = question
    #             while i < variables_amount:
    #                 q = bind_var_to_question(q, instance.variables[i], row[i])
    #                 i = i + 1
    #             result.append(Question(q, row[variables_amount]))

    for q in result:
        print("Q: " + q.question)
        print("A: " + q.answer + "\n")

    # # the QueryProcessor knows the FOAF prefix from the graph
    # # which in turn knows it from reading the N3 RDF file
    # for row in g.query("SELECT ?d WHERE { [] rdf:type ?d}"):
    #     print(row.d)


if __name__ == '__main__':
    main()
