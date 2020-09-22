def pretty_log(function):
    def wrapper(*args):
        result = function(*args)
        file_name = function.__module__.split('.')[-1]
        if len(args):
            print(f'[{file_name.upper()}] - {function.__name__}({",".join(list(args))}) = {result}')
        else:
            print(f'[{file_name.upper()}] - {function.__name__}() = {result}')
        return result
    return wrapper