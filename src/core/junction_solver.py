import math


def _perp(dx, dy):
	L = math.sqrt(dx * dx + dy * dy)
	if L < 1e-8:
		return (0.0, 1.0)
	return (-dy / L, dx / L)


def _line_intersect(p1, d1, p2, d2):
	cross = d1[0] * d2[1] - d1[1] * d2[0]
	if abs(cross) < 1e-10:
		return None
	dx = p2[0] - p1[0]
	dy = p2[1] - p1[1]
	t = (dx * d2[1] - dy * d2[0]) / cross
	return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def _walls_connectable(a, b):
	# Option B groundwork: only walls in the same non-zero connection group are joinable.
	return a.connection_group != 0 and a.connection_group == b.connection_group


def junction_entries(junction, junctions_by_id, sg, target_wall=None):
	# Angularly-sorted entries of walls connected at this junction.
	# When target_wall is provided, keep only walls connectable with target_wall
	# (plus the target itself) so policy filtering can be introduced incrementally.
	jx, jy = junction.position
	entries = []
	for w in sg.get_walls_for_junction(junction.id):
		if target_wall is not None and w.id != target_wall.id and not _walls_connectable(target_wall, w):
			continue
		other_jid = w.junction_end if w.junction_start == junction.id else w.junction_start
		other_j = junctions_by_id.get(other_jid)
		if other_j is None:
			continue
		odx = other_j.position[0] - jx
		ody = other_j.position[1] - jy
		L = math.sqrt(odx * odx + ody * ody)
		if L < 1e-8:
			continue
		out_ux, out_uy = odx / L, ody / L
		out_nx, out_ny = _perp(odx, ody)
		angle = math.atan2(out_uy, out_ux)
		entries.append((angle, w, out_ux, out_uy, out_nx, out_ny, w.thickness / 2.0))

	# Primary order is angular; tie-break by policy and wall id for determinism.
	entries.sort(key=lambda e: (e[0], -e[1].join_priority, e[1].junction_order, e[1].id))
	return entries


def junction_polygon_corners(junction, junctions_by_id, sg):
	jx, jy = junction.position
	entries = junction_entries(junction, junctions_by_id, sg)
	if len(entries) < 3:
		return []

	N = len(entries)
	corners = []
	for i in range(N):
		cur = entries[i]
		nxt = entries[(i + 1) % N]

		cur_left_off = (cur[4] * cur[6], cur[5] * cur[6])
		nxt_right_off = (-nxt[4] * nxt[6], -nxt[5] * nxt[6])

		p1 = (jx + cur_left_off[0], jy + cur_left_off[1])
		p2 = (jx + nxt_right_off[0], jy + nxt_right_off[1])

		pt = _line_intersect(p1, (cur[2], cur[3]), p2, (nxt[2], nxt[3]))
		if pt is None:
			corners.append(p1)
			continue
		corners.append(pt)

	unique = []
	for c in corners:
		if unique and abs(c[0] - unique[-1][0]) < 1e-6 and abs(c[1] - unique[-1][1]) < 1e-6:
			continue
		unique.append(c)
	return unique if len(unique) >= 3 else []


def corner_at_junction(junction, target_wall, is_start, ux, uy, nx, ny, ht,
					   side_off, junctions_by_id, sg):
	jx, jy = junction.position
	raw = (jx + side_off[0], jy + side_off[1])
	wall_dir = (ux, uy) if is_start else (-ux, -uy)

	entries = junction_entries(junction, junctions_by_id, sg, target_wall=target_wall)
	N = len(entries)
	if N < 2:
		return raw

	target_idx = next((i for i, e in enumerate(entries) if e[1].id == target_wall.id), None)
	if target_idx is None:
		return raw

	if N == 2:
		adj_e = entries[(target_idx + 1) % N]
		dot = wall_dir[0] * adj_e[2] + wall_dir[1] * adj_e[3]
		cross = wall_dir[0] * adj_e[3] - wall_dir[1] * adj_e[2]
		if dot < -0.95 and abs(cross) < 0.05:
			return raw

	_on_own_left = (side_off[0] * nx + side_off[1] * ny) > 0
	is_left_side = _on_own_left if is_start else not _on_own_left

	if is_left_side:
		adj_e = entries[(target_idx + 1) % N]
		adj_side_off = (-adj_e[4] * adj_e[6], -adj_e[5] * adj_e[6])
	else:
		adj_e = entries[(target_idx - 1) % N]
		adj_side_off = (adj_e[4] * adj_e[6], adj_e[5] * adj_e[6])

	p_this = raw
	d_this = wall_dir
	p_adj = (jx + adj_side_off[0], jy + adj_side_off[1])
	d_adj = (adj_e[2], adj_e[3])

	pt = _line_intersect(p_this, d_this, p_adj, d_adj)
	if pt is None:
		return raw
	return pt


def compute_wall_quad(wall, junctions_by_id, sg):
	j_start = junctions_by_id.get(wall.junction_start)
	j_end = junctions_by_id.get(wall.junction_end)
	if not (j_start and j_end):
		return None

	sx, sy = j_start.position
	ex, ey = j_end.position
	dx = ex - sx
	dy = ey - sy
	L = math.sqrt(dx * dx + dy * dy)
	if L < 1e-8:
		return None

	ux, uy = dx / L, dy / L
	nx, ny = _perp(dx, dy)
	ht = wall.thickness / 2.0

	left_off = (nx * ht, ny * ht)
	right_off = (-nx * ht, -ny * ht)

	p0 = corner_at_junction(j_start, wall, True, ux, uy, nx, ny, ht, left_off, junctions_by_id, sg)
	p1 = corner_at_junction(j_end, wall, False, ux, uy, nx, ny, ht, left_off, junctions_by_id, sg)
	p2 = corner_at_junction(j_end, wall, False, ux, uy, nx, ny, ht, right_off, junctions_by_id, sg)
	p3 = corner_at_junction(j_start, wall, True, ux, uy, nx, ny, ht, right_off, junctions_by_id, sg)
	return (p0, p1, p2, p3)
