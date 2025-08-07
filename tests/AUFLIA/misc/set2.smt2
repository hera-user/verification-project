(declare-fun x () Int)

(assert (forall ((y Int) (z Int))
    (and
        (> (+ x y) 10)
        (< x 10)
    )
))
