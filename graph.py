class Node:
    def __init__(self, id=0, type='crossing', name='', dir=1):
        self.type = type
        self.neighbours = []
        self.name = name
        self.id = id
        self.weights = []
        self.enabled = True
        self.dir = dir

    def set_neighbour(self, idx, node, weight):
        neigh_no = len(self.neighbours)
        if idx >= neigh_no:
            self.neighbours.extend([None,]*(idx - neigh_no + 1))
            self.weights.extend([float('inf'), ] * (idx - neigh_no + 1))

        self.neighbours[idx] = node
        self.weights[idx] = weight

    def neighbour_number(self):
        return len([neigh for neigh in self.neighbours if neigh is not None])


class Graph():
    @staticmethod
    def get_by_id(graph, id):
        return [node for node in graph if node.id == id]

    @staticmethod
    def get_by_id_desc(desc: dict, id):
        for n in desc['nodes']:
            if n['id'] == id:
                return n

        return None

    @staticmethod
    def check_dict(desc: dict):
        errors = []
        # check ID individuality
        ids = dict()
        for idx, node in enumerate(desc['nodes']):
            if node['id'] not in ids.keys():
                ids[node['id']] = idx
            else:
                errors.append(f'Duplicate IDs: ID of the {idx}th node is already in use by {ids[node["id"]]}')

        for node in desc['nodes']:

            # check weight positiveness
            errors.extend(
                [f'Error in node {node["id"]}: weight to neighbour {idx} is non positive: {neigh[1]}']
                for idx, neigh in enumerate(node['neighbours']) if neigh[1] <= 0)

            # check if name is only 1 character long
            if len(node["name"]) > 1:
                errors.append(f'Error in node {node["id"]}: name can only be 1 character long')

            # check if type is good
            if not node["type"] in ['crossing', 'segment', 'lane_switch', 'dead_end']:
                errors.append(f'Error in node {node["id"]}: invalid type {node["type"]}')

            # Check node symmetry
            for n_w in node['neighbours']:
                if n_w[0] is not None:
                    nbr = Graph.get_by_id_desc(desc, n_w[0])

                    if nbr is None:
                        errors.append(f'No node found by id {n_w[0]}, declared as a neighbour of node {node["id"]}')
                        continue

                    found_at_neighbour = False
                    same_weight_found = False
                    for nbr_n_w in nbr['neighbours']:
                        if nbr_n_w[0] == node["id"]:
                            found_at_neighbour = True
                            if n_w[1] == nbr_n_w[1]:
                                same_weight_found = True


                    if not found_at_neighbour:
                        errors.append(f'Node {node["id"]} is not found in the neighbours of node {nbr["id"]}')
                        continue

                    # if not same_weight_found:
                    #     errors.append(f'No matching weight was found from node {node["id"]} to node {nbr["id"]}')

            # Check if crossing, dead_end and lane_switch has only segment neighbour and vice versa
            if node['type'] in ['crossing', 'dead_end', 'lane_switch']:
                errors.extend([f'Node {node["id"]} should have only segment type neighbour but the {idx}th is not'
                               for idx, n_w in enumerate(node['neighbours']) if
                               n_w[0] is not None and Graph.get_by_id_desc(desc, n_w[0])['type'] != 'segment'])

            # Check if there is 6 neighbours
            if len(node['neighbours']) != 6:
                errors.append(f'Error in node {node["id"]}: not enough neighbours')

            # Check if dead_end has only 1 neighbour and lane_switch and segment has 2
            if node['type'] == 'dead_end':
                not_none_neigh = [n for n in node['neighbours'] if n[0] is not None]
                if len(not_none_neigh) != 1:
                    # errors.append(
                    #     f'Error in node {node["id"]}: {node["type"]} should have only 1 neighbour, {len(not_none_neigh)} was found')
                    pass

            elif node['type'] in ['segment', 'lane_switch']:
                not_none_neigh = [n for n in node['neighbours'] if n[0] is not None]
                if len(not_none_neigh) != 2:
                    # errors.append(
                    #     f'Error in node {node["id"]}: {node["type"]} should have 2 neighbours, {len(not_none_neigh)} was found')
                    pass

        return errors



    @staticmethod
    def fromDict(description: dict):
        nodes_desc = description['nodes']

        graph = []
        # has_cross = False
        for node_desc in nodes_desc:
            if node_desc['name']:
                name = node_desc['name']
            else:
                name = ' '
            graph.append(Node(node_desc['id'], node_desc['type'], name))
            if node_desc['type'] == 'crossing':
                has_cross = True

        # if not has_cross:
        #     crosses = set()
        #     for node_desc in nodes_desc:
        #         for n_w in node_desc['neighbour']:
        #             if n_w[0] is not None:
        #                 crosses.add(n_w[0])
        #
        #     cross_ids = sorted(crosses)
        #     cross_nodes = []
        #     for cross_id in cross_ids:
        #         cross_nodes.append(Node(cross_id, 'crossing'))
        #
        #     idx = len(graph) - 1
        #     while idx > -1 and nodes_desc[idx]['type'] in ['dead_end', 'lane_switch']:
        #         idx = idx-1
        #
        #     if idx < 0:
        #         cross_nodes.extend(graph)
        #         graph = cross_nodes
        #     else:
        #         tmp = graph[0:idx+1] + cross_nodes + graph[idx+1:]
        #         graph = tmp

        for idx, node in enumerate(graph):
            for neigh_idx, n_w in enumerate(nodes_desc[idx]['neighbours']):
                if n_w[0] is not None:
                    node.set_neighbour(neigh_idx, Graph.get_by_id(graph, n_w[0])[0], n_w[1])
                else:
                    node.set_neighbour(neigh_idx, None, float('inf'))

            # if not has_cross:
            #     Graph.get_by_id(graph, neigh_weight[0])[0].set_neighbour()

        return graph