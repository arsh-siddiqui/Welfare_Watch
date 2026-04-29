/* WelfareWatch India Map v5 — State + District Level Dots */

var STATE_COORDS = {
  'Andhra Pradesh':[15.9129,79.74],'Arunachal Pradesh':[28.218,94.7278],
  'Assam':[26.2006,92.9376],'Bihar':[25.0961,85.3131],'Chhattisgarh':[21.2787,81.8661],
  'Goa':[15.2993,74.124],'Gujarat':[22.2587,71.1924],'Haryana':[29.0588,76.0856],
  'Himachal Pradesh':[31.1048,77.1734],'Jharkhand':[23.6102,85.2799],
  'Karnataka':[15.3173,75.7139],'Kerala':[10.8505,76.2711],
  'Madhya Pradesh':[22.9734,78.6569],'Maharashtra':[19.7515,75.7139],
  'Manipur':[24.6637,93.9063],'Meghalaya':[25.467,91.3662],
  'Mizoram':[23.1645,92.9376],'Nagaland':[26.1584,94.5624],
  'Odisha':[20.9517,85.0985],'Punjab':[31.1471,75.3412],
  'Rajasthan':[27.0238,74.2179],'Sikkim':[27.533,88.5122],
  'Tamil Nadu':[11.1271,78.6569],'Telangana':[18.1124,79.0193],
  'Tripura':[23.9408,91.9882],'Uttar Pradesh':[26.8467,80.9462],
  'Uttarakhand':[30.0668,79.0193],'West Bengal':[22.9868,87.855],
  'Delhi':[28.7041,77.1025],'Jammu & Kashmir':[33.7782,76.5762],
  'Ladakh':[34.1526,77.577],'Puducherry':[11.9416,79.8083],
};

var DISTRICT_COORDS = {
  'Andhra Pradesh|Visakhapatnam':[17.6868,83.2185],'Andhra Pradesh|Vijayawada':[16.5062,80.648],
  'Andhra Pradesh|Guntur':[16.3067,80.4365],'Andhra Pradesh|Nellore':[14.4426,79.9865],
  'Andhra Pradesh|Kurnool':[15.8281,78.0373],'Andhra Pradesh|Rajahmundry':[17.005,81.7799],
  'Andhra Pradesh|Tirupati':[13.6288,79.4192],'Andhra Pradesh|Kakinada':[16.9891,82.2475],
  'Andhra Pradesh|Anantapur':[14.6819,77.6006],'Andhra Pradesh|Chittoor':[13.2172,79.1002],
  'Andhra Pradesh|Kadapa':[14.4674,78.8241],'Andhra Pradesh|East Godavari':[17.3264,81.8397],
  'Andhra Pradesh|West Godavari':[16.9174,81.3368],'Andhra Pradesh|Srikakulam':[18.2949,83.8938],
  'Andhra Pradesh|Vizianagaram':[18.1066,83.3956],'Andhra Pradesh|Krishna':[16.5504,80.5283],
  'Andhra Pradesh|Prakasam':[15.9455,80.0282],'Andhra Pradesh|Nandyal':[15.4779,78.4837],
  'Andhra Pradesh|Eluru':[16.7107,81.0952],'Andhra Pradesh|Anakapalli':[17.6924,83.0049],
  'Andhra Pradesh|Konaseema':[16.8178,82.2379],'Andhra Pradesh|Parvathipuram Manyam':[18.7783,83.4297],
  'Andhra Pradesh|Alluri Sitharama Raju':[17.9614,82.5697],'Andhra Pradesh|SPS Nellore':[14.4426,79.9865],
  'Assam|Kamrup Metro':[26.1445,91.7362],'Assam|Dibrugarh':[27.4728,94.912],
  'Assam|Jorhat':[26.7509,94.2037],'Assam|Nagaon':[26.3472,92.6842],
  'Assam|Barpeta':[26.3247,91.0073],'Assam|Cachar':[24.8282,92.7789],
  'Assam|Darrang':[26.4607,92.0413],'Assam|Dhubri':[26.0186,89.9805],
  'Assam|Goalpara':[26.1722,90.6218],'Assam|Golaghat':[26.5177,93.9653],
  'Assam|Hailakandi':[24.6844,92.5696],'Assam|Karimganj':[24.8653,92.3568],
  'Assam|Kokrajhar':[26.4009,90.2772],'Assam|Lakhimpur':[27.2351,94.1015],
  'Assam|Majuli':[27.1728,94.89],'Assam|Morigaon':[26.252,92.3438],
  'Assam|Nalbari':[26.4447,91.438],'Assam|Sivasagar':[26.9847,94.6384],
  'Assam|Sonitpur':[26.6272,92.8025],'Assam|Kamrup':[26.12,91.438],
  'Assam|Assam Zone 1':[26.5,91.5],'Assam|Assam Zone 2':[26.0,92.5],
  'Assam|Assam Zone 3':[27.0,93.5],'Assam|Assam Zone 4':[25.5,92.0],
  'Bihar|Patna':[25.5941,85.1376],'Bihar|Gaya':[24.7914,85.0002],
  'Bihar|Muzaffarpur':[26.1209,85.3647],'Bihar|Bhagalpur':[25.2425,87.0164],
  'Bihar|Darbhanga':[26.1542,85.8918],'Bihar|Araria':[26.1485,87.5278],
  'Bihar|Aurangabad':[24.7522,84.3738],'Bihar|Banka':[24.8797,86.9219],
  'Bihar|Begusarai':[25.4182,86.1297],'Bihar|Buxar':[25.5642,83.98],
  'Bihar|Champaran East':[26.65,84.93],'Bihar|Champaran West':[27.0,84.4],
  'Bihar|Gopalganj':[26.4683,84.4369],'Bihar|Jamui':[24.924,86.224],
  'Bihar|Jehanabad':[25.2175,84.9942],'Bihar|Kaimur':[25.0419,83.6],
  'Bihar|Katihar':[25.5374,87.5712],'Bihar|Khagaria':[25.502,86.4691],
  'Bihar|Kishanganj':[26.1059,87.9422],'Bihar|Lakhisarai':[25.156,86.0981],
  'Bihar|Nalanda':[25.1334,85.4495],'Bihar|Sitamarhi':[26.5881,85.49],
  'Delhi|Central Delhi':[28.6508,77.2167],'Delhi|East Delhi':[28.6392,77.2935],
  'Delhi|North Delhi':[28.7217,77.1757],'Delhi|North East Delhi':[28.6892,77.2969],
  'Delhi|North West Delhi':[28.7304,77.1023],'Delhi|South Delhi':[28.5244,77.1856],
  'Delhi|South East Delhi':[28.5706,77.304],'Delhi|South West Delhi':[28.58,77.08],
  'Delhi|West Delhi':[28.6508,77.053],'Delhi|Shahdara':[28.6741,77.2889],
  'Delhi|Delhi Zone 1':[28.62,77.10],'Delhi|Delhi Zone 2':[28.70,77.20],
  'Delhi|Delhi Zone 3':[28.65,77.30],'Delhi|Delhi Zone 4':[28.55,77.15],
  'Gujarat|Ahmedabad':[23.0225,72.5714],'Gujarat|Surat':[21.1702,72.8311],
  'Gujarat|Vadodara':[22.3072,73.1812],'Gujarat|Rajkot':[22.3039,70.8022],
  'Gujarat|Jamnagar':[22.4707,70.0577],'Gujarat|Gandhinagar':[23.2156,72.6369],
  'Gujarat|Anand':[22.5645,72.9289],'Gujarat|Bhavnagar':[21.7645,72.1519],
  'Gujarat|Junagadh':[21.5222,70.4579],'Gujarat|Kutch':[23.7337,69.8597],
  'Gujarat|Banaskantha':[24.1742,72.0014],'Gujarat|Bharuch':[21.7051,72.9959],
  'Gujarat|Dahod':[22.8363,74.2543],'Gujarat|Kheda':[22.75,72.68],
  'Gujarat|Mahisagar':[23.0932,73.4529],'Gujarat|Ankleshwar':[21.6268,73.0015],
  'Gujarat|Botad':[22.1692,71.6665],'Gujarat|Chhota Udaipur':[22.3066,74.0154],
  'Gujarat|Devbhoomi Dwarka':[22.2394,69.0057],'Gujarat|Gir Somnath':[20.9072,70.3637],
  'Haryana|Gurugram':[28.4595,77.0266],'Haryana|Faridabad':[28.4089,77.3178],
  'Haryana|Ambala':[30.3782,76.7767],'Haryana|Hisar':[29.1492,75.7217],
  'Haryana|Rohtak':[28.8955,76.6066],'Haryana|Karnal':[29.6857,76.9905],
  'Haryana|Sonipat':[28.9931,77.0151],'Haryana|Panipat':[29.3909,76.9635],
  'Haryana|Bhiwani':[28.7975,76.1322],'Haryana|Jhajjar':[28.6082,76.6555],
  'Haryana|Jind':[29.3162,76.3148],'Haryana|Kaithal':[29.802,76.398],
  'Haryana|Kurukshetra':[29.9695,76.8783],'Haryana|Mahendragarh':[28.2691,76.147],
  'Haryana|Mewat':[28.0996,77.0149],'Haryana|Palwal':[28.1444,77.3275],
  'Haryana|Panchkula':[30.6942,76.8606],'Haryana|Rewari':[28.1977,76.6177],
  'Haryana|Fatehabad':[29.518,75.4546],'Haryana|Yamunanagar':[30.129,77.2674],
  'Haryana|Haryana Zone 1':[29.0,76.5],'Haryana|Haryana Zone 2':[29.5,76.0],
  'Haryana|Haryana Zone 3':[28.5,77.0],'Haryana|Haryana Zone 4':[30.0,77.0],
  'Karnataka|Bengaluru':[12.9716,77.5946],'Karnataka|Bengaluru Urban':[12.9716,77.5946],
  'Karnataka|Bengaluru Rural':[13.1986,77.5664],'Karnataka|Mysuru':[12.2958,76.6394],
  'Karnataka|Mangaluru':[12.9141,74.856],'Karnataka|Hubli':[15.3647,75.124],
  'Karnataka|Dharwad':[15.4589,75.0078],'Karnataka|Belagavi':[15.8497,74.4977],
  'Karnataka|Shivamogga':[13.9299,75.5681],'Karnataka|Tumkur':[13.3379,77.1173],
  'Karnataka|Davanagere':[14.4644,75.9218],'Karnataka|Kalaburagi':[17.3297,76.82],
  'Karnataka|Vijayapura':[16.8302,75.71],'Karnataka|Hassan':[13.0068,76.0996],
  'Karnataka|Chikkamagaluru':[13.3161,75.772],'Karnataka|Kodagu':[12.4244,75.7382],
  'Karnataka|Udupi':[13.3409,74.7421],'Karnataka|Dakshina Kannada':[12.8438,75.2479],
  'Karnataka|Uttara Kannada':[14.7941,74.669],'Karnataka|Gadag':[15.4317,75.6267],
  'Karnataka|Haveri':[14.7955,75.4003],'Karnataka|Ramanagara':[12.7157,77.2806],
  'Karnataka|Kolar':[13.136,78.129],'Karnataka|Chikkaballapur':[13.4356,77.7279],
  'Karnataka|Mandya':[12.5218,76.8951],'Karnataka|Chamarajanagar':[11.9261,76.9441],
  'Kerala|Thiruvananthapuram':[8.5241,76.9366],'Kerala|Ernakulam':[9.9816,76.2999],
  'Kerala|Kozhikode':[11.2588,75.7804],'Kerala|Thrissur':[10.5276,76.2144],
  'Kerala|Kollam':[8.8932,76.6141],'Kerala|Kottayam':[9.5916,76.5222],
  'Kerala|Malappuram':[11.051,76.071],'Kerala|Kannur':[11.8745,75.3704],
  'Kerala|Kasaragod':[12.4996,74.9869],'Kerala|Alappuzha':[9.4981,76.3388],
  'Kerala|Palakkad':[10.7867,76.6548],'Kerala|Idukki':[9.9189,77.1025],
  'Kerala|Pathanamthitta':[9.2648,76.787],'Kerala|Wayanad':[11.6854,76.132],
  'Kerala|Kerala Zone 1':[8.7,76.8],'Kerala|Kerala Zone 2':[9.5,77.0],
  'Kerala|Kerala Zone 3':[10.5,76.2],'Kerala|Kerala Zone 4':[11.5,75.7],
  'Madhya Pradesh|Bhopal':[23.2599,77.4126],'Madhya Pradesh|Indore':[22.7196,75.8577],
  'Madhya Pradesh|Jabalpur':[23.1815,79.9864],'Madhya Pradesh|Gwalior':[26.2183,78.1828],
  'Madhya Pradesh|Ujjain':[23.1765,75.7885],'Madhya Pradesh|Sagar':[23.8388,78.7378],
  'Madhya Pradesh|Rewa':[24.5362,81.3036],'Madhya Pradesh|Satna':[24.5682,80.8322],
  'Madhya Pradesh|Vidisha':[23.525,77.813],'Madhya Pradesh|Betul':[21.9139,77.9],
  'Madhya Pradesh|Chhindwara':[22.0574,78.9382],'Madhya Pradesh|Damoh':[23.8367,79.4418],
  'Madhya Pradesh|Dewas':[22.9676,76.0534],'Madhya Pradesh|Dhar':[22.5985,75.3023],
  'Madhya Pradesh|Hoshangabad':[22.75,77.73],'Madhya Pradesh|Katni':[23.8294,80.3964],
  'Madhya Pradesh|Khandwa':[21.8285,76.3527],'Madhya Pradesh|Neemuch':[24.4717,74.8666],
  'Madhya Pradesh|Ratlam':[23.3332,75.038],'Madhya Pradesh|Shivpuri':[25.4231,77.66],
  'Maharashtra|Mumbai':[19.076,72.8777],'Maharashtra|Pune':[18.5204,73.8567],
  'Maharashtra|Nagpur':[21.1458,79.0882],'Maharashtra|Nashik':[19.9975,73.7898],
  'Maharashtra|Aurangabad':[19.8762,75.3433],'Maharashtra|Solapur':[17.6805,75.9064],
  'Maharashtra|Thane':[19.2183,72.9781],'Maharashtra|Kolhapur':[16.705,74.2433],
  'Maharashtra|Amravati':[20.932,77.7523],'Maharashtra|Latur':[18.4088,76.5604],
  'Maharashtra|Ahmednagar':[19.0948,74.748],'Maharashtra|Nanded':[19.1383,77.321],
  'Maharashtra|Buldhana':[20.529,76.184],'Maharashtra|Hingoli':[19.7164,77.1498],
  'Maharashtra|Jalgaon':[21.0077,75.5626],'Maharashtra|Parbhani':[19.2704,76.7735],
  'Maharashtra|Ratnagiri':[16.9902,73.312],'Maharashtra|Satara':[17.6805,73.9875],
  'Maharashtra|Sindhudurg':[16.349,73.9788],'Maharashtra|Osmanabad':[18.186,76.0362],
  'Odisha|Bhubaneswar':[20.2961,85.8245],'Odisha|Cuttack':[20.4625,85.883],
  'Odisha|Puri':[19.8134,85.8315],'Odisha|Rourkela':[22.2604,84.8536],
  'Odisha|Sambalpur':[21.4669,83.9812],'Odisha|Berhampur':[19.315,84.7941],
  'Odisha|Baripada':[21.9324,86.728],'Odisha|Angul':[20.8397,85.1016],
  'Odisha|Balasore':[21.4938,86.9352],'Odisha|Bargarh':[21.3342,83.6216],
  'Odisha|Bolangir':[20.7018,83.4837],'Odisha|Boudh':[20.8393,84.3242],
  'Odisha|Deogarh':[21.5325,84.7336],'Odisha|Dhenkanal':[20.6637,85.598],
  'Odisha|Gajapati':[19.3219,84.04],'Odisha|Ganjam':[19.3873,84.5516],
  'Odisha|Jagatsinghpur':[20.2573,86.1716],'Odisha|Jajpur':[20.8455,86.3351],
  'Odisha|Jharsuguda':[21.8553,84.0075],'Odisha|Koraput':[18.8133,82.7106],
  'Odisha|Odisha Zone 1':[20.0,84.0],'Odisha|Odisha Zone 2':[20.5,85.5],
  'Odisha|Odisha Zone 3':[21.5,84.5],'Odisha|Odisha Zone 4':[19.5,83.0],
  'Punjab|Amritsar':[31.634,74.8723],'Punjab|Ludhiana':[30.901,75.8573],
  'Punjab|Jalandhar':[31.326,75.5762],'Punjab|Patiala':[30.3398,76.3869],
  'Punjab|Bathinda':[30.211,74.9455],'Punjab|Gurdaspur':[32.0413,75.4098],
  'Punjab|Barnala':[30.3781,75.5447],'Punjab|Faridkot':[30.6742,74.7555],
  'Punjab|Fatehgarh Sahib':[30.649,76.393],'Punjab|Ferozepur':[30.9283,74.6199],
  'Punjab|Hoshiarpur':[31.5143,75.9116],'Punjab|Kapurthala':[31.3812,75.381],
  'Punjab|Mansa':[29.9981,75.3949],'Punjab|Moga':[30.8119,75.1668],
  'Punjab|Muktsar':[30.4785,74.5164],'Punjab|Nawanshahr':[31.1262,76.1156],
  'Punjab|Rupnagar':[30.9577,76.5257],'Punjab|SAS Nagar':[30.7046,76.7179],
  'Punjab|Sangrur':[30.245,75.8429],'Punjab|Tarn Taran':[31.4524,74.928],
  'Punjab|Punjab Zone 1':[31.0,74.5],'Punjab|Punjab Zone 2':[31.5,75.0],
  'Punjab|Punjab Zone 3':[30.5,76.0],'Punjab|Punjab Zone 4':[32.0,75.5],
  'Rajasthan|Jaipur':[26.9124,75.7873],'Rajasthan|Jodhpur':[26.2389,73.0243],
  'Rajasthan|Udaipur':[24.5854,73.7125],'Rajasthan|Kota':[25.2138,75.8648],
  'Rajasthan|Ajmer':[26.4521,74.64],'Rajasthan|Bikaner':[28.0229,73.3119],
  'Rajasthan|Alwar':[27.553,76.6346],'Rajasthan|Bharatpur':[27.2152,77.4903],
  'Rajasthan|Barmer':[25.7463,71.3933],'Rajasthan|Bundi':[25.4382,75.6367],
  'Rajasthan|Dausa':[26.8825,76.3254],'Rajasthan|Jalore':[25.3458,72.6144],
  'Rajasthan|Jhalawar':[24.5981,76.1589],'Rajasthan|Karauli':[26.4963,77.0189],
  'Rajasthan|Nagaur':[27.2031,73.733],'Rajasthan|Pali':[25.7711,73.3234],
  'Rajasthan|Sawai Madhopur':[26.015,76.3513],'Rajasthan|Sikar':[27.6094,75.1399],
  'Rajasthan|Sirohi':[24.8864,72.8639],'Rajasthan|Tonk':[26.1669,75.7885],
  'Tamil Nadu|Chennai':[13.0827,80.2707],'Tamil Nadu|Coimbatore':[11.0168,76.9558],
  'Tamil Nadu|Madurai':[9.9252,78.1198],'Tamil Nadu|Tiruchirappalli':[10.7905,78.7047],
  'Tamil Nadu|Salem':[11.6643,78.146],'Tamil Nadu|Tirunelveli':[8.7139,77.7567],
  'Tamil Nadu|Cuddalore':[11.748,79.7714],'Tamil Nadu|Dharmapuri':[12.1274,78.1581],
  'Tamil Nadu|Dindigul':[10.3624,77.9695],'Tamil Nadu|Erode':[11.341,77.7172],
  'Tamil Nadu|Kancheepuram':[12.8185,79.6947],'Tamil Nadu|Krishnagiri':[12.5189,78.2138],
  'Tamil Nadu|Nagapattinam':[10.7672,79.8449],'Tamil Nadu|Ramanathapuram':[9.3762,78.8307],
  'Tamil Nadu|Sivaganga':[9.8497,78.4838],'Tamil Nadu|Thanjavur':[10.7905,79.1378],
  'Tamil Nadu|Thoothukudi':[8.7642,78.1348],'Tamil Nadu|Tiruppur':[11.1085,77.3411],
  'Tamil Nadu|Vellore':[12.9165,79.1325],'Tamil Nadu|Villupuram':[11.9401,79.4861],
  'Telangana|Hyderabad':[17.385,78.4867],'Telangana|Karimnagar':[18.4386,79.1288],
  'Telangana|Warangal Urban':[17.9689,79.5941],'Telangana|Nizamabad':[18.6725,78.0941],
  'Telangana|Nalgonda':[17.0575,79.2683],'Telangana|Adilabad':[19.6652,78.5321],
  'Telangana|Medak':[18.046,78.2706],'Telangana|Rangareddy':[17.3617,78.4294],
  'Telangana|Bhuvanagiri':[17.5031,79.0561],'Telangana|Jagtial':[18.7948,78.9167],
  'Telangana|Jangaon':[17.7242,79.1538],'Telangana|Kamareddy':[18.3218,78.3415],
  'Telangana|Komaram Bheem':[19.4316,79.5935],'Telangana|Mancherial':[18.8762,79.463],
  'Telangana|Medchal':[17.6318,78.5425],'Telangana|Rajanna Sircilla':[18.3861,78.8347],
  'Telangana|Sangareddy':[17.6136,78.0862],'Telangana|Siddipet':[18.1022,78.8521],
  'Telangana|Suryapet':[17.1407,79.6219],'Telangana|Warangal Rural':[18.0,79.4],
  'Telangana|Telangana Zone 1':[18.5,78.5],'Telangana|Telangana Zone 2':[17.5,79.5],
  'Telangana|Telangana Zone 3':[19.0,79.0],'Telangana|Telangana Zone 4':[17.0,78.0],
  'Uttar Pradesh|Lucknow':[26.8467,80.9462],'Uttar Pradesh|Kanpur':[26.4499,80.3319],
  'Uttar Pradesh|Varanasi':[25.3176,82.9739],'Uttar Pradesh|Agra':[27.1767,78.0081],
  'Uttar Pradesh|Prayagraj':[25.4358,81.8463],'Uttar Pradesh|Meerut':[28.9845,77.7064],
  'Uttar Pradesh|Ghaziabad':[28.6692,77.4538],'Uttar Pradesh|Mathura':[27.4924,77.6737],
  'Uttar Pradesh|Bareilly':[28.367,79.4304],'Uttar Pradesh|Aligarh':[27.8974,78.088],
  'Uttar Pradesh|Gorakhpur':[26.7605,83.3731],'Uttar Pradesh|Moradabad':[28.8386,78.7733],
  'Uttar Pradesh|Saharanpur':[29.964,77.5462],'Uttar Pradesh|Shahjahanpur':[27.8832,79.9032],
  'Uttar Pradesh|Firozabad':[27.1592,78.3957],'Uttar Pradesh|Jhansi':[25.4484,78.5685],
  'Uttar Pradesh|Bijnor':[29.3722,78.1354],'Uttar Pradesh|Ayodhya':[26.7992,82.204],
  'Uttar Pradesh|Hapur':[28.729,77.7758],'Uttar Pradesh|Muzaffarnagar':[29.4727,77.7085],
  'Uttar Pradesh|Kanpur Nagar':[26.4499,80.3319],
  'West Bengal|Kolkata':[22.5726,88.3639],'West Bengal|Howrah':[22.5958,88.2636],
  'West Bengal|Darjeeling':[27.041,88.2663],'West Bengal|Jalpaiguri':[26.5449,88.716],
  'West Bengal|Murshidabad':[24.1836,88.277],'West Bengal|Bardhaman':[23.2324,87.8615],
  'West Bengal|Barddhaman':[23.2324,87.8615],'West Bengal|Birbhum':[23.8875,87.5319],
  'West Bengal|Bankura':[23.2502,87.0752],'West Bengal|Purulia':[23.3327,86.3636],
  'West Bengal|Malda':[25.0108,88.1411],'West Bengal|Nadia':[23.4635,88.5592],
  'West Bengal|Hooghly':[22.9024,88.3929],'West Bengal|Cooch Behar':[26.3219,89.4431],
  'West Bengal|Alipurduar':[26.4942,89.5264],'West Bengal|Asansol':[23.6832,86.9753],
  'West Bengal|Durgapur':[23.5204,87.3119],'West Bengal|Kalimpong':[27.0597,88.4678],
  'West Bengal|Siliguri':[26.7271,88.3953],
  'West Bengal|North 24 Parganas':[22.8,88.5],'West Bengal|South 24 Parganas':[22.0,88.3],
  'West Bengal|Paschim Medinipur':[22.4231,87.3236],'West Bengal|Purba Medinipur':[21.9313,87.7309],
  'Jharkhand|Ranchi':[23.3441,85.3096],'Jharkhand|Dhanbad':[23.7957,86.4304],
  'Jharkhand|Jamshedpur':[22.8046,86.2029],'Jharkhand|Hazaribagh':[23.9964,85.3617],
  'Jharkhand|Bokaro':[23.7862,85.9985],'Jharkhand|Giridih':[24.1882,86.2984],
  'Jharkhand|Deoghar':[24.4833,86.6954],'Jharkhand|Dumka':[24.2677,87.2495],
  'Jharkhand|Godda':[24.83,87.21],'Jharkhand|Gumla':[23.0432,84.5399],
  'Jharkhand|Jamtara':[23.9557,86.804],'Jharkhand|Khunti':[23.0751,85.2787],
  'Jharkhand|Koderma':[24.4658,85.5966],'Jharkhand|Latehar':[23.7456,84.4984],
  'Jharkhand|Lohardaga':[23.4384,84.6899],'Jharkhand|Pakur':[24.6348,87.8465],
  'Jharkhand|Ramgarh':[23.6316,85.5147],'Jharkhand|Sahebganj':[25.25,87.64],
  'Jharkhand|Simdega':[22.6167,84.5167],'Jharkhand|Chatra':[24.2093,84.8744],
  'Jharkhand|Jharkhand Zone 1':[23.5,85.0],'Jharkhand|Jharkhand Zone 2':[24.0,86.0],
  'Jharkhand|Jharkhand Zone 3':[23.0,84.5],'Jharkhand|Jharkhand Zone 4':[24.5,87.0],
  'Himachal Pradesh|Shimla':[31.1048,77.1734],'Himachal Pradesh|Kangra':[32.0998,76.2691],
  'Himachal Pradesh|Mandi':[31.7084,76.9318],'Himachal Pradesh|Kullu':[31.9581,77.1095],
  'Himachal Pradesh|Chamba':[32.553,76.1262],'Himachal Pradesh|Una':[31.4686,76.2648],
  'Himachal Pradesh|Hamirpur':[31.6862,76.5217],'Himachal Pradesh|Solan':[30.9045,77.0967],
  'Himachal Pradesh|Sirmaur':[30.5652,77.4744],'Himachal Pradesh|Bilaspur':[31.3322,76.7592],
  'Himachal Pradesh|Kinnaur':[31.5917,78.0],'Himachal Pradesh|Lahaul Spiti':[32.6833,77.4333],
  'Himachal Pradesh|Himachal Zone 1':[31.0,77.0],'Himachal Pradesh|Himachal Zone 2':[31.5,76.5],
  'Himachal Pradesh|Himachal Zone 3':[32.0,77.5],'Himachal Pradesh|Himachal Zone 4':[30.8,77.8],
  'Uttarakhand|Dehradun':[30.3165,78.0322],'Uttarakhand|Haridwar':[29.9457,78.1642],
  'Uttarakhand|Nainital':[29.3803,79.4636],'Uttarakhand|Almora':[29.5971,79.6591],
  'Uttarakhand|Udham Singh Nagar':[29.0012,79.5195],'Uttarakhand|Pauri Garhwal':[29.7967,79.0183],
  'Uttarakhand|Bageshwar':[29.8369,79.7715],'Uttarakhand|Chamoli':[30.4074,79.309],
  'Uttarakhand|Champawat':[29.3323,80.0914],'Uttarakhand|Pithoragarh':[29.5826,80.2132],
  'Uttarakhand|Rudraprayag':[30.2852,78.9817],'Uttarakhand|Tehri Garhwal':[30.3785,78.4822],
  'Uttarakhand|Uttarkashi':[30.7268,78.4354],
  'Uttarakhand|Uttarakhand Zone 1':[30.0,79.0],'Uttarakhand|Uttarakhand Zone 2':[29.5,79.5],
  'Uttarakhand|Uttarakhand Zone 3':[30.5,78.5],'Uttarakhand|Uttarakhand Zone 4':[29.0,80.0],
  'Meghalaya|East Khasi Hills':[25.5788,91.8933],'Meghalaya|East Jaintia Hills':[25.375,92.3578],
  'Meghalaya|West Jaintia Hills':[25.42,92.12],'Meghalaya|Ri Bhoi':[25.8047,91.9709],
  'Meghalaya|West Khasi Hills':[25.35,91.0],
  'Meghalaya|Meghalaya Zone 1':[25.2,91.5],'Meghalaya|Meghalaya Zone 2':[25.5,91.9],
  'Meghalaya|Meghalaya Zone 3':[25.8,92.3],'Meghalaya|Meghalaya Zone 4':[25.1,92.0],
  'Goa|North Goa':[15.4909,73.8278],'Goa|South Goa':[15.1741,74.0412],
  'Goa|Goa Zone 1':[15.3,73.9],'Goa|Goa Zone 2':[15.4,74.0],
  'Goa|Goa Zone 3':[15.1,74.1],'Goa|Goa Zone 4':[15.2,73.8],
  'Manipur|Imphal East':[24.8074,93.9384],'Manipur|Imphal West':[24.788,93.944],
  'Manipur|Bishnupur':[24.6278,93.7733],'Manipur|Churachandpur':[24.3299,93.6824],
  'Manipur|Thoubal':[24.6388,94.0128],
  'Manipur|Manipur Zone 1':[24.5,93.5],'Manipur|Manipur Zone 2':[24.8,93.9],
  'Manipur|Manipur Zone 3':[25.1,94.2],'Manipur|Manipur Zone 4':[24.3,94.0],
  'Mizoram|Aizawl':[23.7307,92.7173],'Mizoram|Champhai':[23.4593,93.3242],
  'Mizoram|Lunglei':[22.8797,92.7369],'Mizoram|Serchhip':[23.3031,92.8478],
  'Mizoram|Mizoram Zone 1':[23.1,92.7],'Mizoram|Mizoram Zone 2':[23.5,92.9],
  'Mizoram|Mizoram Zone 3':[22.9,93.1],'Mizoram|Mizoram Zone 4':[23.7,92.5],
  'Nagaland|Kohima':[25.6751,94.1086],'Nagaland|Dimapur':[25.9042,93.7261],
  'Nagaland|Mokokchung':[26.32,94.51],'Nagaland|Tuensang':[26.2769,94.8267],
  'Nagaland|Wokha':[26.1,94.25],
  'Nagaland|Nagaland Zone 1':[25.9,93.8],'Nagaland|Nagaland Zone 2':[26.2,94.3],
  'Nagaland|Nagaland Zone 3':[26.5,94.7],'Nagaland|Nagaland Zone 4':[25.7,94.0],
  'Arunachal Pradesh|Tawang':[27.586,91.859],'Arunachal Pradesh|West Kameng':[27.25,92.75],
  'Arunachal Pradesh|East Kameng':[27.1,93.2],'Arunachal Pradesh|Papum Pare':[27.1,93.6],
  'Arunachal Pradesh|Longding':[27.3766,95.831],'Arunachal Pradesh|Namsai':[27.67,95.82],
  'Arunachal Pradesh|Pakke-Kessang':[27.0,93.7],'Arunachal Pradesh|Kamle':[27.5,93.5],
  'Arunachal Pradesh|Kurung Kumey':[27.8,93.3],
  'Sikkim|East Sikkim':[27.3389,88.6065],'Sikkim|West Sikkim':[27.2833,88.2833],
  'Sikkim|North Sikkim':[27.9,88.5],'Sikkim|South Sikkim':[27.1437,88.4795],
  'Sikkim|Sikkim Zone 1':[27.3,88.5],'Sikkim|Sikkim Zone 2':[27.6,88.3],
  'Sikkim|Sikkim Zone 3':[27.1,88.6],'Sikkim|Sikkim Zone 4':[27.8,88.7],
  'Tripura|West Tripura':[23.7307,91.4066],'Tripura|East Tripura':[23.8566,91.88],
  'Tripura|North Tripura':[24.4,92.0],'Tripura|South Tripura':[23.1,91.7],
  'Tripura|Khowai':[24.0657,91.6049],
  'Tripura|Tripura Zone 1':[23.5,91.4],'Tripura|Tripura Zone 2':[23.9,91.7],
  'Tripura|Tripura Zone 3':[24.3,92.0],'Tripura|Tripura Zone 4':[23.2,91.9],
  'Jammu & Kashmir|Jammu Zone 1':[32.7,74.8],'Jammu & Kashmir|Jammu Zone 2':[33.7,74.9],
  'Jammu & Kashmir|Jammu Zone 3':[34.0,75.3],'Jammu & Kashmir|Jammu Zone 4':[34.5,76.0],
  'Ladakh|Leh':[34.1526,77.577],'Ladakh|Kargil':[34.5539,76.1349],
  'Puducherry|Puducherry Zone 1':[11.9,79.8],'Puducherry|Puducherry Zone 2':[11.8,79.7],
  'Puducherry|Puducherry Zone 3':[11.7,79.9],'Puducherry|Puducherry Zone 4':[12.0,79.8],
  'Chhattisgarh|Raipur':[21.2514,81.6296],'Chhattisgarh|Bilaspur':[22.0797,82.1409],
  'Chhattisgarh|Durg':[21.1901,81.2849],'Chhattisgarh|Korba':[22.3595,82.7501],
  'Chhattisgarh|Raigarh':[21.9,83.4],'Chhattisgarh|Rajnandgaon':[21.1,81.0],
  'Chhattisgarh|Jagdalpur':[19.0748,82.0174],'Chhattisgarh|Bastar':[19.0748,82.0174],
  'Chhattisgarh|Surguja':[23.1168,83.4],'Chhattisgarh|Surajpur':[23.2,82.9],
  'Chhattisgarh|Baloda Bazar':[21.65,82.16],'Chhattisgarh|Balrampur':[23.7,83.6],
  'Chhattisgarh|Dhamtari':[20.7,81.55],'Chhattisgarh|Gariaband':[20.6,82.0],
  'Chhattisgarh|Janjgir-Champa':[22.0,82.6],'Chhattisgarh|Jashpur':[22.9,84.1],
  'Chhattisgarh|Kabirdham':[22.0,81.3],'Chhattisgarh|Kanker':[20.3,81.5],
  'Chhattisgarh|Mahasamund':[21.1,82.1],'Chhattisgarh|Mungeli':[22.1,81.7],
  'Chhattisgarh|Sukma':[18.4,81.7],
  'Chhattisgarh|Chhattisgarh Zone 1':[21.5,81.5],'Chhattisgarh|Chhattisgarh Zone 2':[22.0,82.0],
  'Chhattisgarh|Chhattisgarh Zone 3':[20.5,81.8],'Chhattisgarh|Chhattisgarh Zone 4':[23.0,83.0],
};

const IND_LABELS=['Education & Literacy','Healthcare Access','Food Security','Employment & Income'];

function scoreColor(v){
  if(v===null||v===undefined) return '#94A3B8';
  if(v>=80) return '#10B981'; if(v>=60) return '#3B82F6';
  if(v>=40) return '#F59E0B'; if(v>=20) return '#F97316';
  return '#EF4444';
}
function scoreLabel(v){
  if(v===null||v===undefined) return 'No Data';
  if(v>=80) return '🌟 Excellent'; if(v>=60) return '✅ Good';
  if(v>=40) return '⚠️ Moderate'; if(v>=20) return '🔶 Weak';
  return '🚨 Critical';
}

function jitteredCoord(key, state){
  if(DISTRICT_COORDS[key]) return DISTRICT_COORDS[key];
  var base = STATE_COORDS[state] || [20, 78];
  var h = 0;
  for(var i=0;i<key.length;i++) h = (h*31 + key.charCodeAt(i)) & 0xffffffff;
  return [base[0]+((h&0xff)/255-0.5)*2.0, base[1]+(((h>>8)&0xff)/255-0.5)*2.5];
}

var stateLayerGroup, districtLayerGroup;

function buildStateLayer(map, stateData){
  stateLayerGroup = L.layerGroup().addTo(map);
  const stateRows=[];
  Object.entries(STATE_COORDS).forEach(([state,coords])=>{
    const info=stateData[state]||{};
    const score=info.score??null; const color=scoreColor(score); const count=info.count||0;
    const circle=L.circleMarker(coords,{radius:13,fillColor:color,color:'#fff',weight:2.5,opacity:1,fillOpacity:.88}).addTo(stateLayerGroup);
    let indRows='';
    ['i1','i2','i3','i4'].forEach((k,i)=>{ if(info[k]!=null){ const ic=scoreColor(info[k]); indRows+=`<div style="display:flex;justify-content:space-between;font-size:12px;margin-top:4px;color:#475569"><span>${IND_LABELS[i]}</span><span style="font-weight:700;color:${ic}">${info[k]}/100</span></div>`; }});
    const tip=`<div style="font-weight:800;font-size:15px;color:#0A1628;margin-bottom:6px">${state}</div><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px"><div><span style="font-family:'Bricolage Grotesque',sans-serif;font-size:28px;font-weight:800;color:${color}">${score??'—'}</span><span style="font-size:13px;color:#94A3B8">/100</span></div><span style="font-size:12px;font-weight:700;color:${color};background:${color}18;padding:4px 9px;border-radius:20px">${scoreLabel(score)}</span></div>${indRows}<div style="margin-top:10px;padding-top:8px;border-top:1px solid #E2E8F0;font-size:11px;color:#94A3B8">${count} districts · Click to view profile</div>`;
    circle.bindTooltip(tip,{permanent:false,direction:'top',offset:[0,-14],opacity:1,className:'ww-tip'});
    circle.on('mouseover',function(){this.setStyle({radius:18,fillOpacity:1})});
    circle.on('mouseout', function(){this.setStyle({radius:13,fillOpacity:.88})});
    circle.on('click',()=>window.location.href='/state/'+encodeURIComponent(state));
    stateRows.push({state,score,color,label:scoreLabel(score),count});
  });
  populateTable(stateRows);
}

function buildDistrictLayer(map){
  if(districtLayerGroup){ districtLayerGroup.addTo(map); return; }
  const loadingEl=document.getElementById('district-loading');
  if(loadingEl) loadingEl.style.display='flex';
  districtLayerGroup = L.layerGroup();
  fetch('/api/district-map-data')
    .then(r=>r.json())
    .then(data=>{
      Object.entries(data).forEach(([key,info])=>{
        const coords=jitteredCoord(key,info.state);
        const color=scoreColor(info.score);
        const circle=L.circleMarker(coords,{radius:6,fillColor:color,color:'#fff',weight:1.5,opacity:1,fillOpacity:.85}).addTo(districtLayerGroup);
        let indRows='';
        [{k:'i1',n:IND_LABELS[0]},{k:'i2',n:IND_LABELS[1]},{k:'i3',n:IND_LABELS[2]},{k:'i4',n:IND_LABELS[3]}].forEach(({k,n})=>{ if(info[k]!=null){ const ic=scoreColor(info[k]); indRows+=`<div style="display:flex;justify-content:space-between;font-size:11px;margin-top:3px;color:#475569"><span>${n}</span><span style="font-weight:700;color:${ic}">${info[k]}/100</span></div>`; }});
        const tip=`<div style="font-weight:800;font-size:14px;color:#0A1628;margin-bottom:2px">${info.district}</div><div style="font-size:11px;color:#64748B;margin-bottom:8px">${info.state}</div><div style="display:flex;align-items:center;gap:10px;margin-bottom:8px"><span style="font-family:'Bricolage Grotesque',sans-serif;font-size:26px;font-weight:800;color:${color}">${info.score??'—'}</span><span style="font-size:11px;font-weight:700;color:${color};background:${color}18;padding:3px 8px;border-radius:20px">${scoreLabel(info.score)}</span></div>${indRows}<div style="margin-top:8px;font-size:10px;color:#94A3B8">Click for full profile</div>`;
        circle.bindTooltip(tip,{permanent:false,direction:'top',offset:[0,-8],opacity:1,className:'ww-tip'});
        circle.on('mouseover',function(){this.setStyle({radius:9,fillOpacity:1})});
        circle.on('mouseout', function(){this.setStyle({radius:6,fillOpacity:.85})});
        circle.on('click',()=>window.location.href='/commentary/district/'+encodeURIComponent(info.district));
      });
      districtLayerGroup.addTo(map);
      if(loadingEl) loadingEl.style.display='none';
    })
    .catch(()=>{ if(loadingEl) loadingEl.style.display='none'; });
}

function populateTable(stateRows){
  const tbody=document.getElementById('stateTableBody');
  if(!tbody) return;
  tbody.innerHTML='';
  stateRows.slice().sort((a,b)=>(b.score??-1)-(a.score??-1)).forEach((item,idx)=>{
    const rank=idx+1; const medal=rank===1?'🥇':rank===2?'🥈':rank===3?'🥉':'';
    tbody.innerHTML+=`<tr><td style="font-weight:600">${medal} <a href="/state/${encodeURIComponent(item.state)}" style="color:var(--p)">${item.state}</a></td><td><div style="display:flex;align-items:center;gap:8px"><div style="flex:1;background:#F1F5F9;border-radius:20px;height:7px"><div style="width:${item.score??0}%;background:${item.color};border-radius:20px;height:7px"></div></div><span style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:14px;color:${item.color};min-width:38px">${item.score??'—'}/100</span></div></td><td><span style="font-size:13px;font-weight:700;color:${item.color}">${item.label}</span></td><td style="color:var(--ts);font-size:13px">${item.count}</td></tr>`;
  });
}

function initMap(stateData){
  const map=L.map('india-map',{center:[22,80],zoom:5,scrollWheelZoom:true});
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{attribution:'© OpenStreetMap © CARTO',subdomains:'abcd',maxZoom:19}).addTo(map);
  const style=document.createElement('style');
  style.textContent=`.ww-tip{background:#fff!important;border:1px solid #E2E8F0!important;border-radius:12px!important;box-shadow:0 4px 24px rgba(0,0,0,.13)!important;padding:14px 16px!important;font-family:'Inter',sans-serif;min-width:200px}.ww-tip::before{display:none!important}`;
  document.head.appendChild(style);
  buildStateLayer(map, stateData);
  const toggleBtn=document.getElementById('toggleViewBtn');
  let mode='state';
  if(toggleBtn){
    toggleBtn.addEventListener('click',()=>{
      if(mode==='state'){
        mode='district'; map.removeLayer(stateLayerGroup); buildDistrictLayer(map);
        toggleBtn.innerHTML='<i class="fa fa-circle-dot"></i> State View';
        toggleBtn.classList.add('btn-p'); toggleBtn.classList.remove('btn-ghost');
        if(document.getElementById('viewModeLabel')) document.getElementById('viewModeLabel').textContent='District Level';
        map.setZoom(6);
      } else {
        mode='state'; if(districtLayerGroup) map.removeLayer(districtLayerGroup);
        stateLayerGroup.addTo(map); toggleBtn.innerHTML='<i class="fa fa-map"></i> District View';
        toggleBtn.classList.remove('btn-p'); toggleBtn.classList.add('btn-ghost');
        if(document.getElementById('viewModeLabel')) document.getElementById('viewModeLabel').textContent='State Level';
        map.setZoom(5);
      }
    });
  }
}
