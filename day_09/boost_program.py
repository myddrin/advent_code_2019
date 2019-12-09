from common.intcode import Program

if __name__ == '__main__':
    test_prog = Program(
        Program.load_memory_from_file('input.txt'),
        inputs=[1],
        dynamic_memory=True,
    )

    test_prog.run()

    print(f'Running test got {", ".join(map(str, test_prog.outputs))}')  # 3638931938

    boost_prog = Program(
        Program.load_memory_from_file('input.txt'),
        inputs=[2],
        dynamic_memory=True,
    )

    boost_prog.run()

    print(f'Running boost got {", ".join(map(str, boost_prog.outputs))}')
