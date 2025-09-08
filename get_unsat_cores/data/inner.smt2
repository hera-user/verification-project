(set-info :smt-lib-version 2.6)
(set-option :auto_config false)
(set-option :type_check true)
(set-option :smt.case_split 3)
(set-option :smt.qi.eager_threshold 100)
(set-option :smt.delay_units true)
(set-option :smt.arith.solver 2)
(set-option :smt.arith.nl false)
(set-option :smt.mbqi false)
(set-option :model.compact false)
(set-option :model.v2 true)
(set-option :pp.bv_literals false)
(set-info :category "industrial")


(declare-fun c () Int)
(declare-fun d () Int)
(declare-fun P (Int) Bool)
(declare-fun R (Int Int) Bool)

(assert
    (forall ((X Int)) (!
        (or
            (P X)
            (forall ((Y Int)) (!
                (R X Y)
                :qid |inner|
                :pattern ((R X Y))
            ))
        )
        :qid |outer|
        :pattern ((P X))
    ))
)

(assert (not (P d)))
(assert (not (P c)))
(assert (not (R c c)))

(check-sat)