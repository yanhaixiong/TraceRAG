import os
import javalang
from datetime import datetime

class ProcessingStats:
    def __init__(self):
        self.processed_files = 0
        self.total_methods = 0
        self.total_variables = 0
        self.failed_files = []
        self.processed_file_details = []

def get_complete_relative_path(input_path, input_folder):
    """获取从 input_folder 开始的相对路径"""
    parts = input_path.split(os.sep)
    input_folder_parts = input_folder.split(os.sep)

    try:
        idx = parts.index(input_folder_parts[-1])
        return os.sep.join(parts[idx+1:])  # 获取相对路径
    except ValueError:
        return input_path

def extract_class_details_with_context_and_save(java_code, input_path, output_root, stats, input_folder):
    try:
        relative_structure = get_complete_relative_path(input_path, input_folder)
        source_file_name = os.path.basename(input_path)

        print(f"\n开始处理文件: {source_file_name}")
        print(f"在路径: {relative_structure}")
        print("=" * 50)

        # 解析 Java 代码
        tree = javalang.parse.parse(java_code)
        code_lines = java_code.splitlines()

        # 获取 package 语句
        package_declaration = ""
        for path, node in tree:
            if isinstance(node, javalang.tree.PackageDeclaration):
                package_declaration = f"package {node.name};\n\n"
                break

        # 创建输出目录
        output_dir = os.path.join(output_root, os.path.dirname(relative_structure))
        source_folder = os.path.join(output_dir, os.path.splitext(source_file_name)[0])

        if not os.path.exists(source_folder):
            os.makedirs(source_folder)
            print(f"创建输出目录: {source_folder}")

        methods_count = 0
        variables_count = 0

        # 遍历 AST，提取变量、方法和内部类
        for path, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration):
                class_name = node.name
                start_line = node.position.line - 1 if node.position else 0
                end_line = start_line
                bracket_count = 0
                for i in range(start_line, len(code_lines)):
                    line = code_lines[i]
                    bracket_count += line.count('{') - line.count('}')
                    end_line = i
                    if bracket_count == 0:
                        break

                class_code = '\n'.join(code_lines[start_line:end_line + 1])

                file_name = f"{class_name}.java"
                file_path = os.path.join(source_folder, file_name)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(package_declaration + class_code)

            elif isinstance(node, javalang.tree.FieldDeclaration):
                try:
                    start_line = node.position.line - 1
                    var_declaration = []
                    for i in range(start_line, len(code_lines)):
                        var_declaration.append(code_lines[i])
                        if ";" in code_lines[i]:
                            break
                    var_code = '\n'.join(var_declaration)
                    for declarator in node.declarators:
                        var_name = declarator.name
                        variables_count += 1

                        file_name = f"{var_name}.java"
                        file_path = os.path.join(source_folder, file_name)
                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(package_declaration + var_code)

                except AttributeError:
                    print("⚠️ 变量声明缺少位置信息，跳过")

            elif isinstance(node, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration)):
                name = node.name if isinstance(node, javalang.tree.MethodDeclaration) else "Constructor"
                methods_count += 1

                print(f"正在处理方法: {name}")

                start_line = node.position.line - 1
                end_line = start_line
                bracket_count = 0
                for i in range(start_line, len(code_lines)):
                    line = code_lines[i]
                    bracket_count += line.count('{') - line.count('}')
                    end_line = i
                    if bracket_count == 0:
                        break

                method_code = '\n'.join(code_lines[start_line:end_line + 1])

                file_name = f"{name}.java"
                file_path = os.path.join(source_folder, file_name)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(package_declaration + method_code)

        # **新增** 处理 public static final class 并独立存储
        for path, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration) and \
               "static" in node.modifiers and "final" in node.modifiers:
                class_name = node.name

                start_line = node.position.line - 1 if node.position else 0
                end_line = start_line
                bracket_count = 0
                for i in range(start_line, len(code_lines)):
                    line = code_lines[i]
                    bracket_count += line.count('{') - line.count('}')
                    end_line = i
                    if bracket_count == 0:
                        break

                class_code = '\n'.join(code_lines[start_line:end_line + 1])

                # 组装完整 Java 文件内容
                full_code = package_declaration + class_code

                # 存储到独立文件
                file_name = f"{class_name}.java"
                file_path = os.path.join(source_folder, file_name)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(full_code)

                print(f"✅ 已提取: {class_name} -> {file_path}")

        print(f"\n文件 {source_file_name} 处理完成:")
        print(f"- 发现变量数量: {variables_count}")
        print(f"- 处理方法数量: {methods_count}")

        stats.processed_files += 1
        stats.total_methods += methods_count
        stats.total_variables += variables_count

    except Exception as e:
        print(f"\n❌ 处理文件 {source_file_name} 时出错: {str(e)}")
        stats.failed_files.append(os.path.join(relative_structure, source_file_name))

def split_java_files(input_folder):
    output_folder = f"{input_folder}_Split"
    print("\n开始处理 Java 文件...")
    print(f"输入目录: {input_folder}")
    print(f"输出目录: {output_folder}")
    print("=" * 50)

    stats = ProcessingStats()
    start_time = datetime.now()

    total_files = sum(1 for _, _, files in os.walk(input_folder) for file in files if file.endswith('.java'))

    print(f"发现 {total_files} 个 Java 文件待处理")

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        java_code = f.read()

                    extract_class_details_with_context_and_save(
                        java_code,
                        file_path,
                        output_folder,
                        stats,
                        input_folder
                    )

                except Exception as e:
                    print(f"❌ 读取文件 {file_path} 时出错: {str(e)}")
                    stats.failed_files.append(file_path)

    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    print("\n✅ 处理完成！")
    print(f"⏳ 总处理时间: {processing_time:.2f} 秒")
    print(f"📂 发现的 Java 文件总数: {total_files}")
    print(f"✅ 成功处理的文件数: {stats.processed_files}")
    print(f"❌ 处理失败的文件数: {len(stats.failed_files)}")




