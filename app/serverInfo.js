'use client'

import { createContext } from 'react';

export const BaseURLContext = createContext(null);
export const CollectionsInfoContext = createContext(null);
export const MobileDeviceContext = createContext(false);
export const SandboxInfoContext = createContext(null);
export const SpeciesInfoContext = createContext([
  {
    "name": "Badger",
    "scientificName": "Taxidea taxus",
    "speciesIconURL": "https://arizona.box.com/shared/static/le9xa515z0h4143xtgjlp4z4w5xy3lgy.jpg",
    "keyBinding": "E"
  },
  {
    "name": "Bear",
    "scientificName": "Ursus americanus",
    "speciesIconURL": "https://arizona.box.com/shared/static/dcxcm0y8u6cnwcz6tftovo68ixkcd2c0.jpg",
    "keyBinding": "B"
  },
  {
    "name": "Bighorn",
    "scientificName": "Ovis Canadensis nelsoni",
    "speciesIconURL": "https://arizona.box.com/shared/static/hr9fbm3b6fnbb8yg8uloymmeji4ja51q.jpg",
    "keyBinding": null
  },
  {
    "name": "Grey Hawk",
    "scientificName": "Buteo plagiatus",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Bobcat",
    "scientificName": "Lynx rufus",
    "speciesIconURL": "https://arizona.box.com/shared/static/wo7la9yp6vjgjxnwna5ohb3wt4xozpf7.jpg",
    "keyBinding": "L"
  },
  {
    "name": "Coatimundi",
    "scientificName": "Nasua narica",
    "speciesIconURL": "https://arizona.box.com/shared/static/2q0f04h3tqiqcexugksleqv26jhv015v.jpg",
    "keyBinding": "O"
  },
  {
    "name": "Cow",
    "scientificName": "Bos tarus",
    "speciesIconURL": "https://arizona.box.com/shared/static/zz058f4tqloy78tfkh7yau4t2org4ey8.jpg",
    "keyBinding": "C"
  },
  {
    "name": "Coyote",
    "scientificName": "Canis latrans",
    "speciesIconURL": "https://arizona.box.com/shared/static/k6zcxzjfymezhjpocmcvl6qrb9dulo0i.jpg",
    "keyBinding": "Y"
  },
  {
    "name": "Domestic Dog",
    "scientificName": "Canis familiaris",
    "speciesIconURL": "https://arizona.box.com/shared/static/bo10uf996fa6cb75c2rbhwla8e3el1tu.jpg",
    "keyBinding": "D"
  },
  {
    "name": "Fox",
    "scientificName": "Urocyon sp. Vulpes spp.",
    "speciesIconURL": "https://arizona.box.com/shared/static/hjjb6d6ysl6ufksfjtvjvyebysm1bvr9.jpg",
    "keyBinding": "F"
  },
  {
    "name": "Ghost",
    "scientificName": "Casper",
    "speciesIconURL": "https://arizona.box.com/shared/static/b68jxx9b364ccklcy3qss5b3eur2imwh.jpg",
    "keyBinding": "G"
  },
  {
    "name": "Gila Monster",
    "scientificName": "Heloderma suspectum",
    "speciesIconURL": "https://arizona.box.com/shared/static/gac34vf3pc83910u6guhslm66gxw5z8k.jpg",
    "keyBinding": null
  },
  {
    "name": "Horse",
    "scientificName": "Equus caballus",
    "speciesIconURL": "https://arizona.box.com/shared/static/0obmlj0j3uo3u4nxgkf8zmpod7eb87w3.jpg",
    "keyBinding": "Q"
  },
  {
    "name": "Human",
    "scientificName": "Homo sapiens",
    "speciesIconURL": "https://arizona.box.com/shared/static/6wb3424e4gqccpn3t58kgaybs2splv41.jpg",
    "keyBinding": "H"
  },
  {
    "name": "Jaguar",
    "scientificName": "Panthera onca",
    "speciesIconURL": "https://arizona.box.com/shared/static/lw9rz5oegolvryos1npm3coteltinw40.jpg",
    "keyBinding": null
  },
  {
    "name": "Javelina",
    "scientificName": "Pecari tajacu",
    "speciesIconURL": "https://arizona.box.com/shared/static/ck0ust0gl7ub4eb8rgsbyujo13zvtmrq.jpg",
    "keyBinding": "J"
  },
  {
    "name": "Lizard",
    "scientificName": "Lacertilia spp.",
    "speciesIconURL": "https://arizona.box.com/shared/static/81ilzi7f26lsmzrq0atb2aojl7uzw40e.jpg",
    "keyBinding": null
  },
  {
    "name": "Deer (Mule)",
    "scientificName": "Odocoileus hemionus",
    "speciesIconURL": "https://arizona.box.com/shared/static/gu5ici81nmmelubnzb602mjg88dhqp8r.jpg",
    "keyBinding": "M"
  },
  {
    "name": "Deer (White-Tailed)",
    "scientificName": "Odocoileus virginianus",
    "speciesIconURL": "https://arizona.box.com/shared/static/9pe69jwbv8z65c9isugtbpak2w6cbn8g.jpg",
    "keyBinding": "W"
  },
  {
    "name": "Ocelot",
    "scientificName": "Leopardus pardalis",
    "speciesIconURL": "https://arizona.box.com/shared/static/9tvofcred8qgy4jmi91dflqtc5r9pbjv.jpg",
    "keyBinding": null
  },
  {
    "name": "Opossum",
    "scientificName": "Didelphis marsupialis",
    "speciesIconURL": "https://arizona.box.com/shared/static/sh0gwe9s907i1ky8f1ezoogbmbh7r4f3.jpg",
    "keyBinding": null
  },
  {
    "name": "Pronghorn",
    "scientificName": "Antilocapra americana",
    "speciesIconURL": "https://arizona.box.com/shared/static/14j5w4drxre29i0vipmo2jgcnnaf5qa1.jpg",
    "keyBinding": null
  },
  {
    "name": "Puma",
    "scientificName": "Puma concolor",
    "speciesIconURL": "https://arizona.box.com/shared/static/nk4mndfkzl48ecpdty65ps34fev3voy6.jpg",
    "keyBinding": "P"
  },
  {
    "name": "Racoon",
    "scientificName": "Procyon lotor",
    "speciesIconURL": "https://arizona.box.com/shared/static/fy4r198unut8yeaockis3iirt12je7z1.jpg",
    "keyBinding": "A"
  },
  {
    "name": "Ringtail",
    "scientificName": "Bassariscus astutus",
    "speciesIconURL": "https://arizona.box.com/shared/static/mfawvlr604jwecqner76aznqxc0403d6.jpg",
    "keyBinding": "N"
  },
  {
    "name": "Rodent",
    "scientificName": "Rodentia",
    "speciesIconURL": "https://arizona.box.com/shared/static/qek2tp6hz88x4l3cmqhy7k8pwu7qwptn.jpg",
    "keyBinding": "Z"
  },
  {
    "name": "Skunk",
    "scientificName": "Mephitis spp. Spilogale sp. Conepatus sp.",
    "speciesIconURL": "https://arizona.box.com/shared/static/mysrtwqnazahzp3jyun58y3c7gpz0qm9.jpg",
    "keyBinding": null
  },
  {
    "name": "Skunk (Hog-Nosed)",
    "scientificName": "Conepatus leuconotus",
    "speciesIconURL": "https://arizona.box.com/shared/static/hpay9f13riudz1bcgvel54xs7i8jlkpg.jpg",
    "keyBinding": null
  },
  {
    "name": "Skunk (Hooded)",
    "scientificName": "Mephitis macroura",
    "speciesIconURL": "https://arizona.box.com/shared/static/ht5ks1kx5lpyg9xnf1amxgaibq9f7r0z.jpg",
    "keyBinding": null
  },
  {
    "name": "Skunk (Striped)",
    "scientificName": "Mephitis mephitis",
    "speciesIconURL": "https://arizona.box.com/shared/static/ff1qzko7jipfr381cjddvtfcf7dc01ig.jpg",
    "keyBinding": null
  },
  {
    "name": "Skunk (Western Spotted)",
    "scientificName": "Spilogale gracilis",
    "speciesIconURL": "https://arizona.box.com/shared/static/kn4qr64s3wfsb6gegscgv4z7461uajpn.jpg",
    "keyBinding": null
  },
  {
    "name": "Sonoran Mud Turtle",
    "scientificName": "Kinosternon sonoriense",
    "speciesIconURL": "https://arizona.box.com/shared/static/q0pzwiow20q8nawmeip2kpbhwk54ev2o.jpg",
    "keyBinding": null
  },
  {
    "name": "Spotted Owl",
    "scientificName": "Strix occidentalis",
    "speciesIconURL": "https://arizona.box.com/shared/static/nd8l4pia5grlymxv1bycsb2mwli80obu.jpg",
    "keyBinding": null
  },
  {
    "name": "Squirrel",
    "scientificName": "Sciurus spp.",
    "speciesIconURL": "https://arizona.box.com/shared/static/w4437lx1wpsgzb55r95e1vajpro5pvsl.jpg",
    "keyBinding": "S"
  },
  {
    "name": "Tortoise",
    "scientificName": "Gopherus morafkai",
    "speciesIconURL": "https://arizona.box.com/shared/static/ahx3293u8j41ejzf4vcwjjwuy7beb155.jpg",
    "keyBinding": null
  },
  {
    "name": "Turkey",
    "scientificName": "Meleagris gallopavo",
    "speciesIconURL": "https://arizona.box.com/shared/static/1xt2pasyyzjkqiirc5pz87uye3duklvy.jpg",
    "keyBinding": "U"
  },
  {
    "name": "Test",
    "scientificName": "Test",
    "speciesIconURL": "https://arizona.box.com/shared/static/9505fzv7yd0vj8dhhwu9p662emmq1fj5.jpg",
    "keyBinding": "T"
  },
  {
    "name": "Frog",
    "scientificName": "Rana Temporaria",
    "speciesIconURL": "https://arizona.box.com/shared/static/y2ebc37cpx31imfvo3buiss632aper59.jpg",
    "keyBinding": null
  },
  {
    "name": "Rabbit (Desert Cottontail)",
    "scientificName": "Sylvilagus audubonii",
    "speciesIconURL": "https://arizona.box.com/shared/static/w2zl2w4j008119ctk1x52aakgroa800f.jpg",
    "keyBinding": null
  },
  {
    "name": "Hare (Black-Tailed Jackrabbit)",
    "scientificName": "Lepus californicus",
    "speciesIconURL": "https://arizona.box.com/shared/static/ygqexm7urzsm1ephi3aov5u5fwx0lzbq.jpg",
    "keyBinding": null
  },
  {
    "name": "Hare (Antelope Jackrabbit)",
    "scientificName": " Lepus alleni",
    "speciesIconURL": "https://arizona.box.com/shared/static/oz0zgd3trb44b7n2kdng9uvq7uawrvxk.jpg",
    "keyBinding": null
  },
  {
    "name": "Hare (Jackrabbits other)",
    "scientificName": "Lepus spp.",
    "speciesIconURL": "https://arizona.box.com/shared/static/yvtfk4554rabw31wspxe0b58f1i0abv4.jpg",
    "keyBinding": null
  },
  {
    "name": "Unknown",
    "scientificName": "Incognita",
    "speciesIconURL": "https://arizona.box.com/shared/static/5i52i7uw79cydn8lrbi74qonbqgxmir3.png",
    "keyBinding": "SLASH"
  },
  {
    "name": "Owl",
    "scientificName": "Strigiformes",
    "speciesIconURL": "https://arizona.box.com/shared/static/m7pnij0v5h21kkhcjifbq9wdb2czn4ck.jpg",
    "keyBinding": null
  },
  {
    "name": "Porcupine",
    "scientificName": "Erethizon dorsatum",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Raptor",
    "scientificName": "Falconiformes",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Insect (flying)",
    "scientificName": "Arthropodus aviator",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Snake",
    "scientificName": "Serpentes",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Caterpillar (moths \u0026 butterflies)",
    "scientificName": "Lepidoptera",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Montezuma Quail",
    "scientificName": "Cyrtonyx montezumae",
    "speciesIconURL": "https://upload.wikimedia.org/wikipedia/commons/e/ea/072_-_MONTEZUMA_QUAIL_%288-20-2014%29_78_circulo_montana%2C_patagonia_lake_ranch_estates%2C_scc%2C_az_-01_%2814805362757%29.jpg",
    "keyBinding": null
  },
  {
    "name": "Rock Squirrel",
    "scientificName": "Otospermophilus variegatus",
    "speciesIconURL": "https://skyislandalliance.org/wp-content/uploads/2020/08/5205548038_bdd96920f0_b.jpg",
    "keyBinding": "V"
  },
  {
    "name": "Bat",
    "scientificName": "Chiroptera",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Bird",
    "scientificName": "Aves",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": "I"
  },
  {
    "name": "Northern Goshawk ",
    "scientificName": "Accipiter Gentilis",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  },
  {
    "name": "Mexican Gray Wolf",
    "scientificName": "Canis lupus baileyi",
    "speciesIconURL": "https://i.imgur.com/4qz5mI0.png",
    "keyBinding": null
  }
]);



export const TokenContext = createContext(null);
