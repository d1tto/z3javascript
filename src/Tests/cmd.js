import Z3 from '../Z3';

const args = process.argv.slice(2);

let b64regex = args[0];

let regex = Buffer.from(b64regex, 'base64').toString('ascii');

regex = new RegExp(regex);

let string = generate(regex);

process.stdout.write(string);

function generate(regex) {
	const ctx = new Z3.Context();
	const solver = new Z3.Solver(ctx, false, []);
	regex = new RegExp(regex);
	let z3Regex = Z3.Regex(ctx, regex);

	let symbolic = ctx.mkConst(ctx.mkStringSymbol('TestC0'), ctx.mkStringSort());
	solver.assert(ctx.mkSeqInRe(symbolic, z3Regex.ast));
	solver.assert(ctx.mkImplies(ctx.mkSeqInRe(symbolic, z3Regex.ast), ctx.mkEq(symbolic, z3Regex.implier)));

	z3Regex.assertions.forEach(assert => {
		solver.assert(assert);
	});

	function Exists(array1, array2, pred) {

		for (let i = 0; i < array1.length; i++) {
			if (pred(array1[i], array2[i])) {
				return true;
			}
		}

		return false;
	}

	function DoesntMatch(l, r) {
		if (l === undefined) {
			return r !== '';
		} else {
			return l !== r;
		}
	}

	function CheckCorrect(model) {
		const real_match = regex.exec(model.eval(symbolic).asConstant());
		const sym_match = z3Regex.captures.map(cap => model.eval(cap).asConstant());
		const matches = real_match && !Exists(real_match, sym_match, DoesntMatch);
		console.log('Matches:', matches, model.eval(symbolic).asConstant(), regex);
		return matches;
	}

	let NotMatch = Z3.Check(CheckCorrect, (query, model) => {
		let query_list = query.exprs.concat([ctx.mkNot(ctx.mkEq(symbolic, ctx.mkString(model.eval(symbolic).asConstant())))]);
		return new Z3.Query(query_list, query.checks);
	});

	let CheckFixed = Z3.Check(CheckCorrect, (query, model) => {
		let real_match = regex.exec(model.eval(symbolic).asConstant());

		if (!real_match) {
			return [];
		} else {

			real_match = regex.exec(model.eval(symbolic).asConstant()).map(match => match || '');
			console.log(`Here ${real_match.length} in ${z3Regex.captures.length}`);

			z3Regex.captures.forEach((x, idx) => {
				console.log(`${x} => ${real_match[idx]}`);
			});

			let query_list = z3Regex.captures.map((cap, idx) => ctx.mkEq(ctx.mkString(real_match[idx]), cap));
			return [new Z3.Query(query.exprs.concat(query_list), [Z3.Check(CheckCorrect, (query, model) => [])])];
		}

	});

	let query = new Z3.Query([], [CheckFixed, NotMatch]);
	//let model = query.getModel(solver);
	let model = solver.getModel();
	if (model) {
		return model.eval(symbolic).asConstant()
	} else {
		return "UNSAT"
	}
}