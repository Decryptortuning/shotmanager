"""Python 3 collection behavior tests without DroneKit or vehicle access."""
import ast
from contextlib import nullcontext
import itertools
from pathlib import Path
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def method(filename, name, namespace):
    path = ROOT / filename
    nodes = [node for node in ast.walk(ast.parse(path.read_text()))
             if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(nodes) == 1
    nodes[0].decorator_list = []
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return namespace[name]


def vector(x, y, z=0):
    return types.SimpleNamespace(x=x, y=y, z=z)


class CurvatureMapTests(unittest.TestCase):
    def test_search_order_in_all_motion_states(self):
        worker = method("cableController.py", "_computeCurvatureMap", {"itertools": itertools})
        for speed, order in [(1, [2, 3, 4, 1, 0]), (-1, [2, 1, 0, 3, 4]), (0, [2, 1, 3, 0, 4])]:
            with self.subTest(speed=speed):
                visited = []
                controller = types.SimpleNamespace(
                    currentP=.5, speed=speed, curvatureMapNumSegments=5,
                    _getCurvatureMapSegment=lambda pos: 2,
                    _computeCurvatureMapSpeedLimit=lambda index: visited.append(index) or False,
                    curvatureMapSegmentsComputedLock=nullcontext(),
                    curvatureMapSegmentsComputed=5, poisonPill=False,
                )
                worker(controller)
                self.assertEqual(visited, order)
                self.assertTrue(controller.poisonPill)


class GeoFenceCollectionTests(unittest.TestCase):
    def test_set_fence_materializes_and_closes_both_polygons(self):
        logger = mock.Mock()
        namespace = {
            "LocationGlobalRelative": lambda lat, lon, alt: types.SimpleNamespace(lat=lat, lon=lon, alt=alt),
            "location_helpers": types.SimpleNamespace(getVectorFromPoints=lambda origin, point: vector(point.lat-origin.lat, point.lon-origin.lon)),
            "GeoFence": lambda origin, points, subpoints, stayOut: types.SimpleNamespace(origin=origin, vertices=points, subVertices=subpoints, stayOut=stayOut),
            "logger": logger,
        }
        setter = method("GeoFenceManager.py", "_handleGeoFenceSetDataMessage", namespace)
        manager = types.SimpleNamespace(polygons=[], _checkGeoFenceDataValidity=lambda *args: True, _sendFenceSetAck=mock.Mock())
        setter(manager, [[(1, 1), (2, 1), (1, 2)]], [[(1.1, 1.1), (1.9, 1.1), (1.1, 1.9)]], [True])
        self.assertEqual(len(manager.polygons), 1)
        fence = manager.polygons[0]
        self.assertEqual(len(fence.vertices), 4)
        self.assertIs(fence.vertices[0], fence.vertices[-1])
        self.assertEqual(len(fence.subVertices), 4)
        self.assertIs(fence.subVertices[0], fence.subVertices[-1])
        self.assertEqual((fence.vertices[1].x, fence.vertices[1].y), (1, 0))
        manager._sendFenceSetAck.assert_called_once_with(1, True)

    def test_fence_geometry_receives_indexable_reusable_lists(self):
        polygons = []
        def inside(point, polygon):
            self.assertEqual(len(polygon), 4)
            self.assertEqual(polygon[0].x, polygon[-1].x)
            polygons.append(polygon)
            return 1
        def collision(*, ray, polygon):
            self.assertIs(polygon, polygons[0])
            self.assertEqual(len(polygon), 4)
            return None
        idle = object()
        activate = method("GeoFenceManager.py", "activateGeoFenceIfNecessary", {
            "Vector2": vector, "Vector3": vector,
            "_GeoFenceManagerTetherState": types.SimpleNamespace(active=object()),
            "location_helpers": types.SimpleNamespace(getVectorFromPoints=lambda *args: vector(.5, .5)),
            "GeoFenceHelper": types.SimpleNamespace(isPointInPolygon=inside, closestCollisionVectorToPolygon=collision),
            "logger": mock.Mock(),
        })
        points = [vector(0, 0), vector(1, 0), vector(0, 1), vector(0, 0)]
        manager = types.SimpleNamespace(
            tetherState=idle,
            vehicle=types.SimpleNamespace(armed=True, system_status="ACTIVE", location=types.SimpleNamespace(global_relative_frame=types.SimpleNamespace(lat=1, lon=1, alt=10)), velocity=[0, 0, 0]),
            polygons=[types.SimpleNamespace(origin=object(), vertices=points, subVertices=points)],
        )
        activate(manager)
        self.assertEqual(len(polygons), 1)


if __name__ == "__main__":
    unittest.main()
