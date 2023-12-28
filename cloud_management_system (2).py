import argparse
import tkinter as tk
from tkinter import ttk, filedialog, Entry, Label, messagebox
import docker
import os

class CloudManagementGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Cloud Management System")
        self.docker_client = docker.from_env()
    
        # Initialize Docker client with a longer timeout
        self.docker_client = docker.from_env(timeout=120)
        self.create_vm_button = ttk.Button(master, text="Create Virtual Machine", command=self.create_virtual_machine_interactive)
        self.create_vm_button.pack(pady=10)

        self.create_dockerfile_button = ttk.Button(master, text="Create Dockerfile", command=self.create_dockerfile_interactive)
        self.create_dockerfile_button.pack(pady=10)

        self.build_image_button = ttk.Button(master, text="Build Docker Image", command=self.build_image_interactive)
        self.build_image_button.pack(pady=10)

        self.list_images_button = ttk.Button(master, text="List Docker Images", command=self.list_images)
        self.list_images_button.pack(pady=10)

        self.list_containers_button = ttk.Button(master, text="List Running Containers", command=self.list_running_containers)
        self.list_containers_button.pack(pady=10)

        self.stop_container_button = ttk.Button(master, text="Stop Container", command=self.stop_container_interactive)
        self.stop_container_button.pack(pady=10)

        self.search_image_button = ttk.Button(master, text="Search Image", command=self.search_image_interactive)
        self.search_image_button.pack(pady=10)

        self.search_hub_image_button = ttk.Button(master, text="Search DockerHub Image", command=self.search_hub_image_interactive)
        self.search_hub_image_button.pack(pady=10)

        self.pull_image_button = ttk.Button(master, text="Pull Docker Image", command=self.pull_image_interactive)
        self.pull_image_button.pack(pady=10)

    def create_virtual_machine_interactive(self):
        input_window = tk.Toplevel(self.master)
        input_window.title("Create Virtual Machine")

        Label(input_window, text="Enter memory size for the VM (MB):").pack()
        memory_entry = Entry(input_window)
        memory_entry.pack()

        Label(input_window, text="Enter disk size for the VM (GB):").pack()
        disk_entry = Entry(input_window)
        disk_entry.pack()

        def handle_click():
            memory = memory_entry.get()
            disk = disk_entry.get()
            if not (memory.isdigit() and disk.isdigit()):
                messagebox.showerror("Error", "Memory and disk values must be positive integers.")
                return

            self.create_virtual_machine(memory, disk)
            input_window.destroy()

        submit_button = tk.Button(input_window, text="Submit", command=handle_click)
        submit_button.pack()

    def create_virtual_machine(self, memory, disk):
        try:
            container = self.docker_client.containers.run(
                image='cloud-management-system:latest',
                detach=True,
                mem_limit=f'{memory}m',
                tty=True
            )
            messagebox.showinfo("Success", f"VM created with ID: {container.id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create VM: {e}")

    def create_dockerfile_interactive(self):
        file_path = filedialog.askdirectory(title="Select Directory to Save Dockerfile")

        input_window = tk.Toplevel(self.master)
        input_window.title("Create Dockerfile")

        Label(input_window, text="Enter the contents of the Dockerfile:").pack()
        contents_entry = Entry(input_window)
        contents_entry.pack()

        def handle_click():
            contents = contents_entry.get()
            self.create_dockerfile(file_path, contents)
            input_window.destroy()

        submit_button = tk.Button(input_window, text="Submit", command=handle_click)
        submit_button.pack()

    def create_dockerfile(self, path, contents):
        dockerfile_path = os.path.join(path, "Dockerfile")
        with open(dockerfile_path, "w") as dockerfile:
            dockerfile.write(contents)
        messagebox.showinfo("Success", f"Dockerfile created at path: {dockerfile_path}")

    def build_image_interactive(self):
        input_window = tk.Toplevel(self.master)
        input_window.title("Build Docker Image")

        Label(input_window, text="Enter the path to the Dockerfile:").pack()
        dockerfile_path_entry = Entry(input_window)
        dockerfile_path_entry.pack()

        Label(input_window, text="Enter the image name and tag:").pack()
        image_name_tag_entry = Entry(input_window)
        image_name_tag_entry.pack()

        def handle_click():
            dockerfile_path = dockerfile_path_entry.get()
            image_name_tag = image_name_tag_entry.get()
            self.build_image(dockerfile_path, image_name_tag)
            input_window.destroy()

        submit_button = tk.Button(input_window, text="Submit", command=handle_click)
        submit_button.pack()

    def build_image(self, dockerfile_path, image_name_tag):
        try:
            self.docker_client.images.build(path=dockerfile_path, tag=image_name_tag)
            messagebox.showinfo("Success", "Docker image built successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to build image: {e}")

    def list_images(self):
        images = self.list_images_docker()
        messagebox.showinfo("List Docker Images", "\n".join(images))

    def list_images_docker(self):
        images = self.docker_client.images.list()
        return [f"Image ID: {image.id}, Tags: {image.tags}" for image in images]

    def list_running_containers(self):
        containers = self.list_running_containers_docker()
        messagebox.showinfo("List Running Containers", "\n".join(containers))

    def list_running_containers_docker(self):
        containers = self.docker_client.containers.list()
        return [f"Container ID: {container.id}, Name: {container.name}" for container in containers]

    def stop_container_interactive(self):
        input_window = tk.Toplevel(self.master)
        input_window.title("Stop Container")

        Label(input_window, text="Enter container ID to stop:").pack()
        container_id_entry = Entry(input_window)
        container_id_entry.pack()

        def handle_click():
            container_id = container_id_entry.get()
            self.stop_container(container_id)
            input_window.destroy()

        submit_button = tk.Button(input_window, text="Submit", command=handle_click)
        submit_button.pack()

    def stop_container(self, container_id):
        try:
            self.docker_client.containers.get(container_id).stop()
            messagebox.showinfo("Success", f"Container {container_id} stopped successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop container: {e}")

    def search_image_interactive(self):
        input_window = tk.Toplevel(self.master)
        input_window.title("Search Image")

        Label(input_window, text="Enter image name to search:").pack()
        image_name_entry = Entry(input_window)
        image_name_entry.pack()

        def handle_click():
            image_name = image_name_entry.get()
            result = self.search_image(image_name)
            messagebox.showinfo("Search Image", "\n".join(result))
            input_window.destroy()

        submit_button = tk.Button(input_window, text="Submit", command=handle_click)
        submit_button.pack()

    def search_image(self, image_name):
        images = self.docker_client.images.search(image_name)
        return [f"Image Name: {image['name']}, Description: {image['description']}" for image in images]

    def search_hub_image_interactive(self):
        input_window = tk.Toplevel(self.master)
        input_window.title("Search DockerHub Image")

        Label(input_window, text="Enter image name to search on DockerHub:").pack()
        hub_image_name_entry = Entry(input_window)
        hub_image_name_entry.pack()

        def handle_click():
            hub_image_name = hub_image_name_entry.get()
            result = self.search_hub_image(hub_image_name)
            messagebox.showinfo("Search DockerHub Image", "\n".join(result))
            input_window.destroy()

        submit_button = tk.Button(input_window, text="Submit", command=handle_click)
        submit_button.pack()

    def search_hub_image(self, hub_image_name):
        images = self.docker_client.images.search(hub_image_name)
        return [f"Image Name: {image['name']}, Description: {image['description']}" for image in images]

    def pull_image_interactive(self):
        input_window = tk.Toplevel(self.master)
        input_window.title("Pull Docker Image")

        Label(input_window, text="Enter the name of the image to pull:").pack()
        pull_image_name_entry = Entry(input_window)
        pull_image_name_entry.pack()

        def handle_click():
            pull_image_name = pull_image_name_entry.get()
            self.pull_image(pull_image_name)
            input_window.destroy()

        submit_button = tk.Button(input_window, text="Submit", command=handle_click)
        submit_button.pack()

    def pull_image(self, image_name):
        try:
            self.docker_client.images.pull(image_name)
            messagebox.showinfo("Success", f"Image {image_name} pulled successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to pull image: {e}")

def main():
    parser = argparse.ArgumentParser(description='Cloud Management System')
    parser.add_argument('--memory', type=int, help='Specify memory size for the VM')
    parser.add_argument('--disk', type=int, help='Specify disk size for the VM')
    parser.add_argument('--config', help='Specify the path to the configuration file')


    args = parser.parse_args()

    if not any(vars(args).values()):
        root = tk.Tk()
        app = CloudManagementGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()