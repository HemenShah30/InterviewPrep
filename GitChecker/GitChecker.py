from git import Repo
import sqlite3 as sql
import sys


def calculate_branch_heads(dir="C:\\Users\\Shah-Desktop\\Documents\\GitHub\\pip"):
    repository = Repo(dir)

    all_references = repository.references

    branch_heads = {}

    for ref in all_references:
        if len(ref.name) > 6 and ref.name[0:6] == "origin":
            branch_heads[ref.name] = ref.commit

    git_info_db_conn = sql.connect("GitInfo.db")
    cursor = git_info_db_conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY,
            branch_name VARCHAR(255) NOT NULL,
            commit_id VARCHAR(255) NOT NULL
        )
    ''')
    cursor.execute('Delete from branches')
    for branch, commit in branch_heads.items():
        cursor.execute('INSERT INTO branches (branch_name, commit_id) VALUES (?,?)', (str(branch), str(commit)))
    git_info_db_conn.commit()

    selected_branches = cursor.execute('Select * from branches')

    print(selected_branches.fetchall())


    git_info_db_conn.close()


def calculate_commit_changes(dir="C:\\Users\\Shah-Desktop\\Documents\\GitHub\\pip"):
    repository = Repo(dir)

    commit_files = {}

    for commit in repository.iter_commits():
        files = []

        commit_tree = commit.tree

        def list_tree_files(subtree, prefix=''):
            for item in subtree:
                path = prefix+item.path
                if item.type == 'blob':
                    files.append(path)
                elif item.type == 'tree':
                    list_tree_files(item, prefix=path + '/')

        list_tree_files(commit_tree)
        commit_files[commit.hexsha] = files
        if len(commit_files) > 30:
            break

    git_info_db_conn = sql.connect("GitInfo.db")
    cursor = git_info_db_conn.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS commit_files (
                commit_id VARCHAR(255) NOT NULL,
                filepath VARCHAR(255) NOT NULL
            )
        ''')

    for commit in commit_files:
        for filepath in commit_files[commit]:
            cursor.execute('insert into commit_files (commit_id, filepath) values (?, ?)', (commit, filepath))

    total_changes = cursor.execute('select commit_id, count(*) from commit_files group by commit_id')

    print(total_changes.fetchall())


if __name__ == "__main__":
    if len(sys.argv) == 2:
        input_git_path = sys.argv[1]
        calculate_branch_heads(input_git_path)
        calculate_commit_changes(input_git_path)
    else:
        calculate_branch_heads()
        calculate_commit_changes()