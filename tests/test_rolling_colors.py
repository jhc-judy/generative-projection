import unittest
import numpy as np
from shaders.shader_03_rolling_colors.simulation import (
    Simulation, COUNT, CYCLE, REBUILD_END, REBUILD_START, PLAY_END, CARD_SIZE,
)


class RollingColorsTests(unittest.TestCase):
    def test_pickup_colors_the_whole_ball_without_patches(self):
        a = Simulation(seed=42)
        a.position = a.grid[0].copy()
        a.collect(0,5.,chain=False)
        a.time = 5.5
        data = a.instances()
        ball = data[data[:,8] == 1]
        self.assertEqual(len(ball),1)
        np.testing.assert_allclose(ball[0,4:7],a.colors[0],atol=1e-6)
        self.assertFalse(np.any(data[:,8] == 2))
        self.assertLessEqual(ball[0,2],CARD_SIZE.min()*1.02)

    def test_frame_rate_independence(self):
        a,b = Simulation(seed=42),Simulation(seed=42)
        for t in np.arange(0,PLAY_END,.15):
            a.advance(float(t))
        b.advance(float(t))
        np.testing.assert_array_equal(a.picked,b.picked)
        np.testing.assert_allclose(a.position,b.position)
        np.testing.assert_allclose(a.local,b.local)
        self.assertGreater(len(a.pickup_order),10)
        self.assertEqual(len(a.pickup_order),len(set(a.pickup_order)))

    def test_rebuilt_grid_matches_next_cycle(self):
        a=Simulation(seed=9)
        a.advance(REBUILD_END)
        cards=a.instances()[1:]
        self.assertEqual(len(cards),COUNT)
        np.testing.assert_allclose(cards[:,:2],a.destinations,atol=1e-6)
        np.testing.assert_allclose(cards[:,2:4],np.tile(CARD_SIZE,(COUNT,1)),atol=1e-6)
        np.testing.assert_allclose(cards[:,7],0,atol=1e-6)
        final={tuple(np.round(pos,5)):color for pos,color in zip(a.destinations,a.colors)}
        a.advance(CYCLE)
        self.assertEqual(len(a.pickup_order),0)
        for pos,color in zip(a.grid,a.colors):
            np.testing.assert_array_equal(final[tuple(np.round(pos,5))],color)

    def test_one_pickup_at_a_time_and_thinking_pauses(self):
        a=Simulation(seed=2)
        stationary=0
        max_speed=0.
        for t in np.arange(5,PLAY_END,.05):
            a.advance(float(t))
            max_speed=max(max_speed,np.linalg.norm(a.velocity))
            stationary += int(np.linalg.norm(a.velocity)<.003)
            active=(a.picked>=0)&(t-a.picked<.42)
            self.assertLessEqual(np.count_nonzero(active),1)
        picked=np.sort(a.picked[a.picked>=0])
        self.assertTrue(np.all(np.diff(picked)>=.60-1e-6))
        self.assertGreater(stationary,40)
        self.assertLess(max_speed,.16)

    def test_reorganization_is_bijective_and_stable(self):
        a=Simulation(seed=18)
        a.advance(REBUILD_START)
        self.assertEqual(len(np.unique(a.destinations,axis=0)),COUNT)
        original=a.rebuild_sources.copy()
        a.advance(REBUILD_START+2)
        np.testing.assert_array_equal(original,a.rebuild_sources)
        self.assertTrue(np.isfinite(a.instances()).all())
        a.advance(CYCLE*2+12)
        self.assertEqual(a.cycle_index,2)


if __name__ == '__main__':
    unittest.main()
