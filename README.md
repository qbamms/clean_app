# cleaning-application



## Getting started

 ## Phase 1: 
 
 The Initial Micro-Launch (The "Simple" Stage)To guarantee operational control and high service quality, limit your initial deployment across three strict dimensions:┌────────────────────────────────────────────────────────────────────────┐
│                        THE LAUNCHPAD MVP                               │
├───────────────────┬──────────────────────────────┬─────────────────────┤
│  1. ONE REGION    │      2. ONE CLIENT TYPE      │  3. ONE SERVICE     │
│  (e.g., Downtown) │      (Residential Only)      │  (Standard Clean)   │
└───────────────────┴──────────────────────────────┴─────────────────────┘

Geographic Focus: Restrict your app to a single city center or 2–3 high-density postcodes. 
Do not expand until you can fill bookings there consistently.

Target Audience: Focus exclusively on B2C Residential Homes. 
Homeowners and renters book faster, require less legal red tape, and provide immediate feedback.

Service Scope: Offer only Standard Domestic Cleaning. 
Avoid complex jobs like post-construction or biohazard cleanings until your operational foundation is solid.

💻 Technical Adaptation for your Python CoreTo keep your initial database and code simple, collapse your matching logic down to a fixed "Per-Hour Unit Marketplace". Remove complex real-time variable calendars and match users based on a simple, flat-rate hourly model.

## Phase 2: 

The Systematic Scaling RoadmapOnce your core residential engine runs reliably and generates consistent positive cash flow, use this sequential order to integrate advanced features and new business verticals:  
[ PHASE 1: LAUNCH ]  ──►  [ PHASE 2: B2B EXPANSION ]  ──►  [ PHASE 3: HORIZONTAL SCALING ]
  • Standard Home Clean     • Office & Office Contracts      • Specialized Deep Cleaning
  • Manual matching         • Invoicing & B2B Portals        • Laundry / Ironing Add-ons
  • Localized Postcodes     • Regional Expansion             • On-Demand Window/Carpet Gear


## Step 1: 

Transition into B2B (Businesses & Organisations)The Upgrade: Introduce corporate office cleaning.The Value: B2B shifts your app from highly volatile weekend bookings to predictable, recurring, weekday contracts (e.g., every Monday/Wednesday/Friday at 6:00 PM).Tech Requirement: Add a Corporate Billing Module into your Python backend to handle monthly paper invoicing, VAT tracking, and multi-user company accounts.

## Step 2: 

Introduce Specialised Tiered ServicesThe Upgrade: Add specialty clean types directly into your user interface selection screen.End of Tenancy / Moving Cleaning (High margin, strict completion checklists).Post-Construction/Renovation Cleaning (Heavy-duty dust/debris extraction).Eco-Friendly/Green Cleaning (Premium tier using certified non-toxic agents).Tech Requirement: Update your ServiceType engine to allow workers to check boxes indicating which premium certifications they possess, allowing them to charge higher rates for specialized tasks.

## Step 3: 

Horizontal Service Stacking (Beyond Cleaning)The Upgrade: Transform your cleaning marketplace into a comprehensive property management ecosystem.Laundry & Ironing delivery (Pick up clothes during the clean, return them next visit).Home Organisation & Decluttering (Closet management, packing/unpacking help).Minor Handyman/Maintenance Tasks (Changing lightbulbs, fixing cabinet hinges).

## Tech Requirement: 

Upgrade your booking architecture to support "Add-On Cart Line Items", letting clients stack secondary tasks onto a primary cleaner's visit.


## Actionable Next Steps to Build the MVP

To get this prototype running as a true testable app without writing a complex frontend, use Streamlit (a pure Python web app framework).

To align your application with the MVP strategy, the code below narrows the operational scope exclusively to Birmingham City Centre postcodes (B1, B2, B3, B4, and B5). 

It focuses purely on Residential Home Cleaning, simplifies worker scheduling to clear 2-hour blocks, and transitions the system from temporary memory to a local, persistent SQLite Database (marketplace.db).

This allows your application to save clients, workers, and bookings locally on your machine without requiring a heavy external database server.

## 1. The SQLite Database Setup (database.py)

Run this script once to initialize your persistent database tables, automatically creating the data structure with built-in Birmingham postcode validation.

## 2. The MVP Marketplace Core Engine (engine.py)

This script contains your core business operations. It strictly validates that clients are based in central Birmingham and programmatically ensures workers are matched by both their postcode zone and active availability().

## 3. Operational Simulation Run (test.py)

Run this file to run through an end-to-end simulation of your MVP platform in action—from validating a local Birmingham client to completing a transactional booking(onboarding clients, managing shifts, filtering by postcode, checking out, and verifying that the booked slot is locked out).

## Requirements.txt file:
This contains necesarry python Libraries used in the scripts.