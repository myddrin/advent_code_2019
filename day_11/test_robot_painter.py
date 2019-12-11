from day_11.robot_painter import Position, RobotPainter


def test_position_sanity():
    assert hash(Position(0, 0)) == hash(Position(0, 0))


def test_question_1():
    robot = RobotPainter()
    robot.run()
    assert len(robot.hull.keys()) == 1951
