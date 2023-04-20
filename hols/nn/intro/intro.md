# Introduction

Estimated Time: 5-10 minutes

## Overview

One day, I woke up and said: how hard could it be to integrate Machine Learning into Gaming, an industry where everything is already software? I started researching the most popular games and, with some gaming experience I had growing up, I decided to look deeper into League of Legends.

Long story short, after some months of developing my League of Legends API wrapper (making calls to the official API with functions I created myself), I started extracting data from professional players with the hopes of creating a Machine Learning predictor that would tell me how I was performing in a match **during and after** the match itself.

This is what this workshop is going to teach you.

We're going to create two models:
- _Offline Model_: we'll obtain after-match data, and compare how well we did to pàst professional games. This will be a good model to **theorize** about which characters are good/bad in the long run.
- _Live Client Model_: we'll obtain **real-time** data from a match, run it through our model, and return a winning probability (0-100)%.

## Introduction to League of Legends

League of Legends is a team-based strategy game in which two teams of five powerful champions face off to destroy the other’s base. As a player, you can choose from over 140 champions to make epic plays, secure kills, and take down towers as you battle your way to victory. To win, you'll need to destroy the enemy’s Nexus—the heart of each team's base.

Access and mobility play an important role in LoL. Your team needs to clear at least one lane to access the enemy Nexus. Blocking your path are defense structures called turrets and inhibitors. Each lane has three turrets and one inhibitor, and each Nexus is guarded by two turrets. In between the lanes is the jungle, where neutral monsters and jungle plants reside. The two most important monsters are Baron Nashor and the Drakes. Killing these units grants unique buffs for your team and can also turn the tide of the game.

Team composition depends on five positions. Each lane lends itself to certain kinds of champions and roles—try them all or lock into the lane that calls you. Champions get stronger by earning experience to level up and buy more powerful items as the game progresses. Staying on top of these two factors is crucial to overpowering the enemy team and destroying their base.

![Bought Items](images/bought_items.jpg)

This image represents the final functionality of one of the two models we'll explore in this workshop, where we use our already-trained ML model to make __real-time__ predictions about our in-game performances. 

Here's a short 3-minute introductory video to League of Legends:

[Watch the video](youtube:OfYU4gbk13w)

### Prerequisites

* An [Oracle Free Tier, Paid or LiveLabs Cloud Account](https://signup.cloud.oracle.com/?language=en&sourceType=:ow:de:ce::::RC_WWMK220210P00063:LoL_handsonLab_introduction&intcmp=:ow:de:ce::::RC_WWMK220210P00063:LoL_handsonLab_introduction)
* Active Oracle Cloud Account with available credits to use for Data Science service.

## About Product/Technology

OCI Data Science is a fully managed and serverless platform for data science teams to build, train, and manage machine learning models using Oracle Cloud Infrastructure.

The Data Science Service:

- Provides data scientists with a collaborative, project-driven workspace.
- Enables self-service, serverless access to infrastructure for data science workloads.
- Helps data scientists concentrate on methodology and domain expertise to deliver models to production.

## Objectives

In this lab, you will complete the following steps:

&check; Understand what a Neural Network is and how it works

&check; Creating an ML model

&check; Web Sockets / Data Streaming Techniques 

&check; Integrating ML Models with Data Pipelines


## OCI Elements

This solution is designed to work with several OCI services, allowing you to quickly be up and running. You can read more about the services used in the lab here:

- [OCI Data Science](https://www.oracle.com/artificial-intelligence/)
- [OCI Cloud Shell](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/cloudshellintro.htm)
- [OCI Compute](https://www.oracle.com/cloud/compute/)
- [OCI Autonomous JSON Database](https://www.oracle.com/autonomous-database/autonomous-json-database/)


You may now [proceed to the next lab](#next).

## Annex - Additional Resources
If you have extra time after this workshop and want to get to know more about League of Legends, we recommend reading these lists of articles to get a feel of everything that can be done in the ML + Gaming space:

1. [Article 1](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/articles/article1.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Data Extraction & Processing
2. [Article 2](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/articles/article2.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Data Extraction & Processing II
3. [Article 3](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/articles/article3.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Building an Adversarial League of Legends AI Model
4. [Article 4](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/articles/article4.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Real-Time predictions
5. [Article 5](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/articles/article5.md): League of Legends Optimizer using Oracle Cloud Infrastructure: Real-Time predictions II


## Acknowledgements

* **Author** - Nacho Martinez, Data Science Advocate @ DevRel
* **Contributors** -  Victor Martin, Product Strategy Director
* **Last Updated By/Date** - April 20th, 2023