import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import pandas as pd
import networkx as nx
from tabulate import tabulate

# 初始化图结构与数据
G = nx.Graph()
locations = {}

def load_data():
    try:
        nodes_df = pd.read_csv("nodes.csv", encoding='utf-8')
        nodes_df.rename(columns={"weight": "visit_time"}, inplace=True)
        #print(nodes_df.columns)

        for _, row in nodes_df.iterrows():
            name = str(row["name"]).strip()
            locations[name] = {
                "type": str(row["type"]).strip(),
                "visit_time": int(row["visit_time"])
            }
            G.add_node(name)

        edges_df = pd.read_csv("edges.csv", encoding='utf-8')
        #print(edges_df.columns)
        for _, row in edges_df.iterrows():
            G.add_edge(str(row["node"]).strip(), str(row["node.1"]).strip(), weight=int(row["weight"]))

    except Exception as e:
        messagebox.showerror("加载失败", f"加载时出错: {e}")




class CampusNavigationGUI:
    def __init__(self, master):
        self.master = master
        master.title("校园路径导航系统")
        master.geometry("1000x700")

        tk.Label(master, text="华东师范大学校园路径导航系统", font=("Arial", 16, "bold")).pack(pady=10)

        frame = tk.Frame(master)
        frame.pack(pady=10)

        features = [
            ("显示所有地点", self.display_locations),
            ("查询地点", self.search_locations),
            ("添加地点", self.add_location),
            ("删除地点", self.delete_location),
            ("修改地点", self.modify_location),
            ("显示所有路径", self.display_paths),
            ("添加路径", self.add_path),
            ("删除路径", self.delete_path),
            ("修改路径", self.modify_path),
            ("检查图连通性", self.check_connectivity),
            ("查找连通的地点", self.find_neighbours),
            ("查询最短路径是否存在", self.check_shortest_path),
            ("查找最短路径", self.find_shortest_path),
            ("最小生成树", self.minimum_spanning_tree),
            ("检查是否存在欧拉通路", self.check_eulerian),
            ("指定地点类型的游览路线", self.location_type_tour),
            ("退出", master.quit)
        ]

        for i, (label, cmd) in enumerate(features):
            btn = tk.Button(frame, text=label, width=25, height=2, command=cmd)
            btn.grid(row=i // 3, column=i % 3, padx=10, pady=5)

        # 结果展示区
        self.output_text = scrolledtext.ScrolledText(master, width=100, height=25, font=("Consolas", 10))
        self.output_text.pack(padx=10, pady=10)

    def clear_output(self):   # 输入一个新指令之后清除之前输出框中的内容
        self.output_text.delete("1.0", tk.END)

    def append_output(self, text):  # 文字输出后自动滚动到最后一行
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)

    def display_locations(self):
        self.clear_output()
        table = [[name, info["type"], info["visit_time"]] for name, info in locations.items()]
        if not table:
            self.append_output("无地点数据。")
            return
        self.append_output(tabulate(table, headers=["名称", "类型", "建议访问时间(分钟)"], tablefmt="simple"))

    def search_locations(self):
        query = simpledialog.askstring("查询地点", "请输入地点名称或类型：", parent=self.master)
        if query is None or query.strip() == "":
            return
        query = query.lower()
        results = [[name, info["type"], info["visit_time"]] for name, info in locations.items()
                   if query == info["type"].lower() or query == name]

        self.clear_output()
        if results:
            self.append_output(tabulate(results, headers=["名称", "类型", "建议访问时间(分钟)"], tablefmt="simple"))
        else:
            self.append_output("未找到匹配地点。")

    def add_location(self):
        name = simpledialog.askstring("添加地点", "请输入地点名称：", parent=self.master)
        if not name:
            return
        name = name.strip()
        if name in locations:
            messagebox.showwarning("添加失败", "地点已存在。")
            return
        loc_type = simpledialog.askstring("添加地点", "请输入地点类型：", parent=self.master)
        if not loc_type:
            return
        try:
            visit_time = simpledialog.askinteger("添加地点", "请输入建议访问时间(分钟)：", parent=self.master, minvalue=0)
            if visit_time is None:
                return
        except Exception:
            messagebox.showerror("添加失败")
            return
        locations[name] = {"type": loc_type.strip(), "visit_time": visit_time}
        G.add_node(name)
        self.append_output(f"成功添加地点：{name}")

    def delete_location(self):
        name = simpledialog.askstring("删除地点", "请输入要删除的地点名称：", parent=self.master)
        if not name:
            return
        name = name.strip()
        if name not in locations:
            messagebox.showwarning("删除失败", "地点不存在。")
            return
        del locations[name]
        if G.has_node(name):
            G.remove_node(name)
        self.append_output(f"成功删除地点：{name}")

    def modify_location(self):
        name = simpledialog.askstring("修改地点", "请输入要修改的地点名称：", parent=self.master)
        if not name:
            return
        name = name.strip()
        if name not in locations:
            messagebox.showwarning("修改失败", "地点不存在。")
            return
        loc_type = simpledialog.askstring("修改地点", f"输入新类型（当前：{locations[name]['type']}）：", parent=self.master)
        if not loc_type:
            return
        visit_time = simpledialog.askinteger("修改地点", f"输入新建议访问时间(分钟)（当前：{locations[name]['visit_time']}）：", parent=self.master, minvalue=0)
        if visit_time is None:
            return
        locations[name] = {"type": loc_type.strip(), "visit_time": visit_time}
        self.append_output(f"成功修改地点：{name}")

    def display_paths(self):
        self.clear_output()
        edges = [[u, v, G[u][v]["weight"]] for u, v in G.edges()]
        if not edges:
            self.append_output("无路径数据。")
            return
        edges.sort(key=lambda x: x[2])   # 按两点之间的距离由小到大排序
        self.append_output(tabulate(edges, headers=["节点1", "节点2", "距离(米)"], tablefmt="simple"))

    def add_path(self):
        node1 = simpledialog.askstring("添加路径", "请输入起点名称：", parent=self.master)
        if not node1:
            return
        node2 = simpledialog.askstring("添加路径", "请输入终点名称：", parent=self.master)
        if not node2:
            return
        node1 = node1.strip()
        node2 = node2.strip()
        if node1 not in locations or node2 not in locations:
            messagebox.showwarning("添加失败", "起点或终点不存在。")
            return
        weight = simpledialog.askinteger("添加路径", "请输入路径距离(米)：", parent=self.master, minvalue=1)
        if weight is None:
            return
        G.add_edge(node1, node2, weight=weight)
        self.append_output(f"成功添加路径：{node1} <-> {node2}，距离{weight}米")

    def delete_path(self):
        node1 = simpledialog.askstring("删除路径", "请输入路径起点名称：", parent=self.master)
        if not node1:
            return
        node2 = simpledialog.askstring("删除路径", "请输入路径终点名称：", parent=self.master)
        if not node2:
            return
        node1 = node1.strip()
        node2 = node2.strip()
        if not G.has_edge(node1, node2):
            messagebox.showwarning("删除失败", "路径不存在。")
            return
        G.remove_edge(node1, node2)
        self.append_output(f"成功删除路径：{node1} <-> {node2}")

    def modify_path(self):
        node1 = simpledialog.askstring("修改路径", "请输入路径起点名称：", parent=self.master)
        if not node1:
            return
        node2 = simpledialog.askstring("修改路径", "请输入路径终点名称：", parent=self.master)
        if not node2:
            return
        node1 = node1.strip()
        node2 = node2.strip()
        if not G.has_edge(node1, node2):
            messagebox.showwarning("修改失败", "路径不存在。")
            return
        current_weight = G[node1][node2]["weight"]
        weight = simpledialog.askinteger("修改路径", f"请输入新距离(米)，当前距离为{current_weight}：", parent=self.master, minvalue=1)
        if weight is None:
            return
        G[node1][node2]["weight"] = weight
        self.append_output(f"成功修改路径：{node1} <-> {node2}，新距离{weight}米")

    def check_connectivity(self):
        self.clear_output()
        if nx.is_connected(G):
            self.append_output("图是连通的。")
        else:
            components = list(nx.connected_components(G))  # 列出所有的连通分量
            self.append_output(f"图不连通，发现 {len(components)} 个连通分量。")
            new_edges = []
            for i in range(len(components) - 1):
                node1 = list(components[i])[0]
                node2 = list(components[i + 1])[0]
                new_edges.append((node1, node2, 100))
            self.append_output("建议添加以下边以连接图：")
            self.append_output(tabulate(new_edges, headers=["节点1", "节点2", "建议距离(米)"], tablefmt="simple"))

    def find_neighbours(self):
        node = simpledialog.askstring("查询连通地点","输入想要查询的地点：", parent = self.master)
        if not node:
            return
        node = node.strip()
        self.clear_output()
        if not node in G:
            self.append_output("该地点不存在。")
            return

        neighbors = list(G.neighbors(node))
        if neighbors:
            self.append_output(f"{node} 的连通地点：{'、'.join(neighbors)}")
        else:
            self.append_output(f"{node} 没有连通地点。")

    def check_shortest_path(self):
        node1 = simpledialog.askstring("查询最短路径存在", "请输入起点名称：", parent=self.master)
        if not node1:
            return
        node2 = simpledialog.askstring("查询最短路径存在", "请输入终点名称：", parent=self.master)
        if not node2:
            return
        node1 = node1.strip()
        node2 = node2.strip()
        self.clear_output()
        if not (node1 in G and node2 in G):
            self.append_output("起点或终点不存在于图中。")
            return
        if nx.has_path(G, node1, node2):  # 如果存在通路，则一定存在最短路径
            self.append_output(f"存在从 {node1} 到 {node2} 的最短路径。")
        else:
            self.append_output(f"不存在从 {node1} 到 {node2} 的路径。")

    def find_shortest_path(self):
        node1 = simpledialog.askstring("查找最短路径", "请输入起点名称：", parent=self.master)
        if not node1:
            return
        node2 = simpledialog.askstring("查找最短路径", "请输入终点名称：", parent=self.master)
        if not node2:
            return
        node1 = node1.strip()
        node2 = node2.strip()
        self.clear_output()
        if not (node1 in G and node2 in G):
            self.append_output("起点或终点不存在于图中。")
            return
        try:
            path = nx.shortest_path(G, node1, node2, weight="weight")
            length = nx.shortest_path_length(G, node1, node2, weight="weight")
            self.append_output(f"从 {node1} 到 {node2} 的最短路径为（距离：{length}米）：")
            self.append_output(" -> ".join(path))
        except nx.NetworkXNoPath:
            self.append_output(f"不存在从 {node1} 到 {node2} 的路径。")

    def minimum_spanning_tree(self):
        self.clear_output()
        if G.number_of_edges() == 0:
            self.append_output("图中无路径数据，无法计算最小生成树。")
            return
        if not nx.is_connected(G):
            self.append_output("图不连通，不存在最小生成树")
            return
        mst = nx.minimum_spanning_tree(G)
        edges = [[u, v, mst[u][v]["weight"]] for u, v in mst.edges()]
        # 计算最小生成树的总权重
        total_weight = sum(mst[u][v]["weight"] for u, v in mst.edges())
        self.append_output(f"最小生成树的总长度:{total_weight} 米")
        self.append_output("最小生成树边如下：")
        self.append_output(tabulate(edges, headers=["节点1", "节点2", "距离(米)"], tablefmt="simple"))

    def check_eulerian(self):
        self.clear_output()

        if G.number_of_edges() == 0:
            self.append_output("图中无路径数据。")
            return

        if not nx.is_connected(G):
            self.append_output("不存在欧拉通路。")
            return

        odd_degree_count = sum(1 for node in G.nodes() if G.degree(node) % 2 == 1)

        if odd_degree_count <= 2:
            self.append_output("存在欧拉通路。")
        else:
            self.append_output("不存在欧拉通路。")

    def location_type_tour(self):
        self.clear_output()
        location_type = simpledialog.askstring("游览路线", "请输入要游览的地点类型：", parent=self.master)

        if location_type is None:  # User canceled the dialog
            self.append_output("未输入地点类型。")
            return

        type_locations = [name for name, info in locations.items() if info["type"] == location_type]

        if not type_locations:
            self.append_output(f"没有找到类型为 {location_type} 的地点数据。")
            return

        subgraph = G.subgraph(type_locations).copy()

        if not nx.is_connected(subgraph.to_undirected()):
            self.append_output(f"类型为 {location_type} 的地点之间不连通，无法规划游览路线。")
            return

        def dfs_path(graph, start, visited=None, path=None):
            if visited is None:
                visited = set()
            if path is None:
                path = []
            visited.add(start)
            path.append(start)
            for neighbor in graph.neighbors(start):
                if neighbor not in visited:
                    dfs_path(graph, neighbor, visited, path)
            return path

        start_node = type_locations[0]
        tour_path = dfs_path(subgraph, start_node)

        self.append_output(f"类型为 {location_type} 的游览路线（非最短，仅一条可行路径）:")
        self.append_output(" -> ".join(tour_path))

if __name__ == "__main__":
    load_data()
    root = tk.Tk()
    gui = CampusNavigationGUI(root)
    root.mainloop()
