params = {

    #----------
    "cat2": {
    #----------
        "ggh": {
            130: dict(
                # sigma0_min = 0.8,
                # sigma1_min = 0.8,
                ),

            },


        }, # cat2

    #----------
    "cat5": {
    #----------
        "vbf": {
            125: dict(
                sigma0_min = 1,
                sigma1_min = 1,
                ),

            140: dict(
                sigma0_min = 1,
                sigma1_min = 1,
                ),

            150: dict(
                sigma0_min = 1,
                sigma1_min = 1,
                ),
            }

        }, # cat7

    #----------
    "cat6": {
    #----------
        "vbf": {
            115: dict(
                sigma0_min = 1,
                sigma1_min = 1,

                sigma0_max = 3,
                sigma1_max = 3,


                ),
            150: dict(
                sigma0_min = 4,
                sigma1_min = 4,

                )
            }

        }, # cat7


    #----------
    "cat7": {
    #----------
        "ggh": {
            115: dict(
                sigma0_min = 2,
                sigma1_min = 2,

                ),

            125: dict(
                sigma0_min = 1,
                sigma1_min = 1,
                
                ),

            140: dict(
                sigma0_max = 6,
                sigma1_max = 6,
                # 
                sigma0_min = 1,
                sigma1_min = 1,

                ),

            }, # ggh

    

        }, # cat7

    #----------
    "cat8": {
    #----------
        "ggh": {
            120: dict(
                sigma0_min = 2,
                sigma1_min = 2,

                ),
            }, # ggh

        "vbf": {
            125: dict(
                sigma0_max = 8,
                sigma1_max = 8,

                ),

            130: dict(
                dmu0_min = -1,
                dmu1_min = -1,

                sigma0_min = 2,
                sigma1_min = 2,

                ),
            }, # vbf

    

        }, # cat8

    #----------
    "cat9": {
    #----------
        "ggh": {
            115: dict(
                sigma0_min = 0.5,
                sigma1_min = 0.5,

                ),
            }, # ggh


        }, # cat9

    #----------
    "cat10": {
    #----------
        "ggh": {
            115: dict(
                dmu0_min = -0.8,
                dmu1_min = -0.8,

                sigma0_min = 0.5,
                sigma1_min = 0.5,


                ),
            120: dict(
                # dmu0_min = -0.8,
                # dmu1_min = -0.8,

                sigma0_min = 0.5,
                sigma1_min = 0.5,


                ),
            }, # ggh


        }, # cat10

    #----------


    }
